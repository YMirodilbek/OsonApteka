from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from Product.decorator import is_staff
from django.contrib import messages
from . import models
from .forms import AboutUsForm
import logging

# Get logger for tmp app
logger = logging.getLogger('tmp')

# Create your views here.

def Vacancy(request):
    vacancy = models.Vacancy.objects.all()
    context = {
        'vacancy':vacancy
    }
    return render(request,'new/vacancy.html',context)


def VacancyApplication(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        age = request.POST.get('age')
        doc = request.FILES.get('doc')
        vacan = models.VacancyApplication.objects.create(fullname=fullname,age=age,doc=doc)
        vacan.type='vacancy'
        vacan.save()
        messages.success(request,'Application submitted successfully')
    return redirect(request.META.get('HTTP_REFERER'))

def ApplicantViwe(request):
    if request.method == 'POST':
        fio = request.POST.get('fio')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        education = request.POST.get('education')
        last_job = request.POST.get('last_job')
        desired_salary = request.POST.get('desired_salary')
        phone_number = request.POST.get('phone_number')
        # document = request.FILES.get('document')  # agar fayl yuborilsa

        models.Applicant.objects.create(
            fio=fio,
            date_of_birth=date_of_birth,
            address=address,
            education=education,
            last_job=last_job,
            desired_salary=desired_salary,
            phone_number=phone_number,
            # document=document
        )
        messages.success(request,'Application submitted successfully')
    return redirect(request.META.get('HTTP_REFERER'))







@login_required(login_url='/auth/send-otp/')
@is_staff
def vacancyCreate(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        age = request.POST.get('age')
        address = request.POST.get('address')
        shift = request.POST.get('shift')
        salary = request.POST.get('salary')
        phone_number = request.POST.get('phone_number')

        logger.info(f"Creating new vacancy: {title} by user {request.user.phone_number}")
        models.Vacancy.objects.create(title=title,age=age,address=address,shift=shift,salary=salary,phone_number=phone_number)
        logger.info(f"Vacancy '{title}' created successfully")
        messages.success(request,'Vacancy created successfully')

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/auth/send-otp/')
@is_staff
def vacancyUpdate(request,id):
    vacancy = models.Vacancy.objects.get(id=id)
    if request.method == 'POST':
        title = request.POST.get('title')
        age = request.POST.get('age')
        address = request.POST.get('address')
        shift = request.POST.get('shift')
        salary = request.POST.get('salary')
        phone_number = request.POST.get('phone_number')
        vacancy.title = title if title else vacancy.title
        vacancy.age = age if age else vacancy.age
        vacancy.address = address if address else vacancy.address
        vacancy.shift = shift if shift else vacancy.shift
        vacancy.salary = salary if salary else vacancy.salary
        vacancy.phone_number = phone_number if phone_number else vacancy.phone_number
        vacancy.save()
        messages.success(request,'Vacancy updated successfully')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def vacancyDelete(request,id):
    vacancy = models.Vacancy.objects.get(id=id)
    vacancy.delete()
    messages.success(request,'Vacancy deleted successfully')
    return redirect(request.META.get('HTTP_REFERER'))



def Pharm(request):
    pharm = models.OurPharmacie.objects.all()
    
    context = {
        'pharm':pharm
    }
    return render(request,'new/farmaset.html',context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def pharmCreate(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        shift = request.POST.get('shift')
        phone_number = request.POST.get('phone_number')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        models.OurPharmacie.objects.create(title=title,address=address,shift=shift,phone_number=phone_number,lat=lat,lon=lon)
        messages.success(request,'Pharmacy created successfully')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def pharmUpdate(request,id):
    pharm = models.OurPharmacie.objects.get(id=id)
    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        shift = request.POST.get('shift')
        phone_number = request.POST.get('phone_number')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        pharm.title = title if title else pharm.title
        pharm.address = address if address else pharm.address
        pharm.shift = shift if shift else pharm.shift
        pharm.phone_number = phone_number if phone_number else pharm.phone_number
        pharm.lat = lat if lat else pharm.lat
        pharm.lon = lon if lon else pharm.lon
        pharm.save()
        messages.success(request,'Pharmacy updated successfully')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def pharmDelete(request,id):
    pharm = models.OurPharmacie.objects.get(id=id)
    pharm.delete()
    messages.success(request,'Pharmacy deleted successfully')
    return redirect(request.META.get('HTTP_REFERER'))



def About(request):
    about = models.AboutUs.objects.all().order_by('order')
    video = models.AboutUsVideo.objects.last()
    context = {
        'about':about,
        'video':video
    }
    return render(request,'new/onas.html',context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_about_video(request):
    video = models.AboutUsVideo.objects.last()
    context = {
        'video':video
    }
    return render(request,'website_dashboard/about_video.html',context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_about_video_update(request):
    video = models.AboutUsVideo.objects.last()
    if video:
        video.video = request.POST.get('video')
        video.save()
        messages.success(request,'Video updated successfully')
    else:
        models.AboutUsVideo.objects.create(video=request.POST.get('video'))
        messages.success(request,'Video created successfully')

    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def aboutUpdate(request, id):
    about = models.AboutUs.objects.get(id=id)
    
    if request.method == 'POST':
        form = AboutUsForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'About updated successfully')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = AboutUsForm(instance=about)
    
    context = {
        'about': about,
        'form': form
    }
    return render(request, 'website_dashboard/about_detail.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def aboutCreate(request):
    if request.method == 'POST':
        form = AboutUsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'About created successfully')
            return redirect('dashboard_about_url')
    else:
        form = AboutUsForm()
    
    return redirect('dashboard_about_url')

@login_required(login_url='/auth/send-otp/')
@is_staff
def aboutDelete(request,id):
    about = models.AboutUs.objects.get(id=id)
    about.delete()
    messages.success(request,'About deleted successfully')
    return redirect('dashboard_about_url')


@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_about_detail(request,id):
    about = models.AboutUs.objects.get(id=id)
    form = AboutUsForm(instance=about)
    context = {
        'about': about,
        'form': form
    }
    return render(request,'website_dashboard/about_detail.html',context)



def Public(request):
    public = models.Public.objects.last()
    context = {
        'public':public
    }
    return render(request,'new/oferta.html',context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def publicUpdate(request):
    public = models.Public.objects.last()
    body = request.POST.get('body')
    if public:
        public.body = body if body else public.body
        public.save()
        messages.success(request,'Public updated successfully')
    else:
        models.Public.objects.create(body=body)
        messages.success(request,'Public created successfully')
    return redirect(request.META.get('HTTP_REFERER'))


def Landlords(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        address = request.POST.get('address')
        phone_number_1 = request.POST.get('phone_number_1')
        email = request.POST.get('email')
        contact_person = request.POST.get('contact_person')
        area = request.POST.get('area')
        comment = request.POST.get('comment')
        models.Landlord.objects.create(city=city,address=address,phone_number_1=phone_number_1,email=email,contact_person=contact_person,area=area,comment=comment)
        messages.success(request,'Sorov qabul qilindi !')
   
    return render(request,'new/arendatelim.html')


@login_required(login_url='/auth/send-otp/')
@is_staff
def landlordUpdate(request,id):
    landlord = models.Landlord.objects.get(id=id)
    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        phone_number_1 = request.POST.get('phone_number_1')
        phone_number_2 = request.POST.get('phone_number_2')
        landlord.title = title if title else landlord.title
        landlord.address = address if address else landlord.address
        landlord.phone_number_1 = phone_number_1 if phone_number_1 else landlord.phone_number_1
        landlord.phone_number_2 = phone_number_2 if phone_number_2 else landlord.phone_number_2
        landlord.save()
        messages.success(request,'Landlord updated successfully')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def landlordDelete(request,id):
    landlord = models.Landlord.objects.get(id=id)
    landlord.delete()
    messages.success(request,'Landlord deleted successfully')
    return redirect(request.META.get('HTTP_REFERER'))



def blog_view(request):
    blogs = models.Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blogs, 10)  # Show 6 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'blogs': page_obj,
    }
    return render(request,'blog/blog.html', context)


def BlogDetail(request, pk):
    blog = models.Blog.objects.get(pk=pk)
    context = {
        'blog': blog
    }
    return render(request, 'blog/blog-details.html', context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def blog_create(request):
    if not request.user.is_staff:
        return redirect('blog')

    if request.method == "POST":
        image = request.FILES.get('image')
        title = request.POST.get('title')
        text = request.POST.get('text')
        models.Blog.objects.create(image=image, title=title, text=text)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/auth/send-otp/')
@is_staff
def blog_update(request,id):
    blog = models.Blog.objects.get(id=id)
    if request.method == 'POST':
        image = request.FILES.get('image')
        title = request.POST.get('title')
        text = request.POST.get('text')
        blog.image = image if image else blog.image
        blog.title = title if title else blog.title
        blog.text = text if text else blog.text
        blog.save()
        messages.success(request,'Blog updated successfully')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/auth/send-otp/')
@is_staff
def blog_delete(request,id):
    blog = models.Blog.objects.get(id=id)
    blog.delete()
    messages.success(request,'Blog deleted successfully')
    return redirect(request.META.get('HTTP_REFERER'))


# Dashboard views
@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard(request):
    context = {
        'vacancy': models.Vacancy.objects.all(),
        'pharm': models.OurPharmacie.objects.all(),
        'landlords': models.Landlord.objects.all(),
    }
    return render(request, 'website_dashboard/index.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_vacancy(request):
    vacancy = models.Vacancy.objects.all()
    context = {
        'vacancy': vacancy
    }
    return render(request, 'website_dashboard/vacancy.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_vacany_application(request):
    vacancy_application = models.VacancyApplication.objects.filter(type='vacancy')
    context = {
        'vacancy_application': vacancy_application
    }
    return render(request, 'website_dashboard/vacancy_application.html', context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_vacancy_application_delete(request,id):
    vacancy_application = models.VacancyApplication.objects.get(id=id)
    vacancy_application.delete()
    messages.success(request,'Vacancy application deleted successfully')
    return redirect(request.META.get('HTTP_REFERER'))
    

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_pharmacy(request):
    pharm = models.OurPharmacie.objects.all()
    context = {
        'pharm': pharm
    }
    return render(request, 'website_dashboard/pharmacy.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_landlords(request):
    landlords = models.Landlord.objects.all()
    context = {
        'landlords': landlords
    }
    return render(request, 'website_dashboard/landlords.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_about(request):
    about = models.AboutUs.objects.all().order_by('order')
    form = AboutUsForm()
    context = {
        'about': about,
        'form': form
    }
    return render(request, 'website_dashboard/about.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_public(request):
    public = models.Public.objects.last()
    context = {
        'public': public
    }
    return render(request, 'website_dashboard/public.html', context)

@login_required(login_url='/auth/send-otp/')
@is_staff
def dashboard_blog(request):
    blogs = models.Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blogs, 10)  # Show 6 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'blogs': page_obj,
    }
    return render(request, 'website_dashboard/blog.html', context)

