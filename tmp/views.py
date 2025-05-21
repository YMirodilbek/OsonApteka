from django.shortcuts import render,redirect
from . import models
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from Product.decorator import is_staff

# Create your views here.

def Vacancy(request):
    vacancy = models.Vacancy.objects.all()
    context = {
        'vacancy':vacancy
    }
    return render(request,'new/vacancy.html',context)


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
        models.Vacancy.objects.create(title=title,age=age,address=address,shift=shift,salary=salary,phone_number=phone_number)
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
    about = models.AboutUs.objects.last()
    context = {
        'about':about
    }
    return render(request,'new/onas.html',context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def aboutUpdate(request):
    about = models.AboutUs.objects.last()
    body = request.POST.get('body')

    if about:
        about.body = body if body else about.body
        about.save()
        messages.success(request,'About updated successfully')
    else:
        models.AboutUs.objects.create(body=body)
        messages.success(request,'About created successfully')
    return redirect(request.META.get('HTTP_REFERER'))


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
    landlords = models.Landlord.objects.all()
    context = {
        'landlords':landlords
    }
    return render(request,'new/arendatelim.html',context)


@login_required(login_url='/auth/send-otp/')
@is_staff
def landlordCreate(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        phone_number_1 = request.POST.get('phone_number_1')
        phone_number_2 = request.POST.get('phone_number_2')
        models.Landlord.objects.create(title=title,address=address,phone_number_1=phone_number_1,phone_number_2=phone_number_2)
        messages.success(request,'Landlord created successfully')
    return redirect(request.META.get('HTTP_REFERER'))

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
    about = models.AboutUs.objects.last()
    context = {
        'about': about
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

