from .forms import PhoneNumberForm, OTPForm, UserDetailsForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import *
import requests
import random
import re


def clean_phone_number(phone_number):
    """Telefon raqamini 998XXXXXXXXX formatiga o'tkazish"""
    phone_number = re.sub(r'\D', '', phone_number)  
    
    if phone_number.startswith("998") and len(phone_number) == 12:
        return phone_number 
    elif phone_number.startswith("9") and len(phone_number) == 9:
        return "998" + phone_number  
    elif phone_number.startswith("0") and len(phone_number) == 10:
        return "998" + phone_number[1:] 
    else:
        return None 
    

def get_eskiz_token():

    token  = EskizToken.objects.last()
    if token and timezone.now() - token.created_at < timedelta(hours=24):
        return token.token

    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {
        "email": "akmalfarmsanoat@mail.ru",  
        "password": "eZ77mhFdKIGEH9ulaJEodkEbKhV79X20UZnODEbZ" 
    }
   
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        token = response.json().get("data", {}).get("token")
        data = response.json()

    if "data" in data and "token" in data["data"]:
        new_token = data["data"]["token"]
        EskizToken.objects.all().delete()  # eski tokenlarni o‘chirish
        EskizToken.objects.create(token=new_token)  # yangisini saqlash
        return new_token
    else:
        raise Exception(f"Eskiz token olishda xatolik: {data}")



def send_sms(phone_number, code):
    """Eskiz orqali SMS yuborish"""
    token = get_eskiz_token()
    if not token:
        return {"error": "Eskiz API tokenini olishda xatolik!"}

    url = "https://notify.eskiz.uz/api/message/sms/send"
    
    headers = {"Authorization": f"Bearer {token}"}

    phone_number = phone_number.replace("+", "").replace(" ", "").strip()
    if not phone_number.startswith("998") or len(phone_number) != 12:
        return {"error": "Telefon raqami noto‘g‘ri formatda!"}
    payload = {
    "mobile_phone": phone_number, 
    "message": f"АКМАЛ FARM Kirish kodingiz: {code}",
    "from": "4546",  
    "callback_url": "" 
    }

    response = requests.post(url, headers=headers, data=payload)
    print("Eskizdan javob:", response.json())  
    return response.json()


def can_send_otp(phone_number):
    """Tasdiqlash kodini qayta yuborishni cheklash"""
    last_sent = cache.get(f"otp_sent_time_{phone_number}")
    if last_sent:
        return False 

    cache.set(f"otp_sent_time_{phone_number}", True, timeout=120)   
    return True


def send_otp(request):
    """Foydalanuvchiga tasdiqlash kodini yuborish"""
    if request.method == "POST":
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            is_agreed = form.cleaned_data['is_agreed']
            print("Telefon raqami:", phone_number)  

            if not can_send_otp(phone_number):
                form.add_error(None, "Tasdiqlash kodini qayta so‘rash uchun biroz kuting!")
                return render(request, 'auth/phone.html', {'form': form})

            otp = random.randint(1000, 9999)
            cache.set(f"otp_{phone_number}", otp, timeout=300)           
            response = send_sms(phone_number, otp)

            if "error" in response:
                form.add_error(None, f"SMS yuborishda xatolik: {response['error']}")
                return render(request, 'auth/phone.html', {'form': form})

            request.session['phone_number'] = phone_number
            request.session['is_agreed'] = is_agreed
            return redirect('verify_otp')

    else:
        form = PhoneNumberForm()

    return render(request, 'auth/phone.html', {'form': form, 'pdf': PDFDocument.objects.first()})


def verify_otp(request):
    """Foydalanuvchi OTP kodini tasdiqlaydi"""
    phone_number = request.session.get('phone_number')
    is_agreed = request.session.get('is_agreed', False)

    if not phone_number:
        return redirect('send_otp')

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            stored_otp = cache.get(f"otp_{phone_number}")

            if stored_otp and str(stored_otp) == otp:
                user, created = CustomUser.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={'is_agree': is_agreed}
                )

                if not created:
                    user.is_agree = True
                    user.save()
                    request.session['user'] = user.phone_number

                login(request, user)
                return redirect('complete_registration')

            else:
                form.add_error('otp', "Noto‘g‘ri tasdiqlash kodi!")

    return render(request, 'auth/verify.html', {'form': OTPForm(), 'phone_number': phone_number})


@login_required
def complete_registration(request):

    if request.method == "POST":
        form = UserDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = UserDetailsForm(instance=request.user)

    return render(request, 'auth/complete.html', {'form': form})

def success(request):
    return render(request, 'index.html')


def Product(request):
    return render(request,'about.html')

def Logout(request):
    logout(request)
    return redirect('/auth/send-otp/')

def blog_view(request):
    blogs = Blog.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request,'blog/blog.html', context)

def BlogDetail(request, pk):
    blog = Blog.objects.get(pk=pk)
    context = {
        'blog': blog
    }
    return render(request, 'blog/blog-details.html', context)