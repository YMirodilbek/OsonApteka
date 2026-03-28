from django.db import models
from ckeditor.fields import RichTextField 


class OurPharmacie(models.Model):
    region = models.CharField(max_length=55,default='Андижан')
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)

    def __str__(self):
        return self.title


class Landlord(models.Model):
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    phone_number_1 = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.title
    

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    fio = models.CharField("ФИО", max_length=255)
    date_of_birth = models.CharField("Дата рождения",max_length=55)
    address = models.CharField("Адрес проживания", max_length=255)
    education = models.CharField("Образование", max_length=255)
    last_job = models.CharField("Последнее место работы", max_length=255, blank=True, null=True)
    desired_salary = models.DecimalField("Желаемая зарплата", max_digits=12, decimal_places=2)
    phone_number = models.CharField("Номер телефона для связи", max_length=20)

    def __str__(self):
        return self.fio


class VacancyApplication(models.Model):
    TYPE = (
        ('vacancy','vacancy'),
        ('anketu','anketu'),
    )
    fullname = models.CharField(max_length = 255)
    age = models.CharField(max_length=510)
    doc = models.FileField(upload_to='vacancy_docs/')
    type = models.CharField(max_length=55,  choices=TYPE, null=True, blank=True)
    def __str__(self):
        return self.fullname


class AboutUs(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    body = RichTextField(
        config_name='default',
        default='',
        blank=True,
        verbose_name='About Us'
    )
    image = models.ImageField(upload_to='about_us/', null=True, blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return "About Us"
    

class AboutUsVideo(models.Model):
    video = models.URLField(max_length=255)

    def __str__(self):
        return "About Us Video"


class Public(models.Model):
    body = models.TextField()

    def __str__(self):
        return "Public"


class Blog(models.Model):
    image = models.ImageField(upload_to='blog/')
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        return super().delete(using, keep_parents)

    def save(self, *args, **kwargs):
        if self.pk:
            old_image = Blog.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                old_image.delete(save=False)

        super().save(*args, **kwargs)
    

class GlavniImage(models.Model):
    img = models.ImageField(upload_to='glavni/')
    

class Sertificate(models.Model):
    name =  models.CharField(max_length=55)
    last_name =  models.CharField(max_length=55)
    n = models.DecimalField(decimal_places=0, max_digits=5)
    date = models.DateField()
    director = models.CharField(max_length=255)
    psixologiya = models.PositiveIntegerField()
    Farmokologiya = models.PositiveIntegerField()
    Amaliyot = models.PositiveIntegerField()
    good_grade = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    
    @property
    def n_(self):
        return f"{int(self.n):04d}"

