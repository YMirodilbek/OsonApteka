from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField 
from django.utils.timezone import now
from main.models import CustomUser
from django.db import models
from main.models import *

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255)
    svg = models.ImageField(upload_to="svg/",null=True, blank=True )
    def __str__(self):
        return self.name


class Member(models.Model):
    name = models.CharField(max_length=155)
    def __str__(self):
        return self.name

 
class Product(models.Model):
    
    PERSON_CHOICES  = (
        ('bolalar','bolalar'),
        ('ayollar','ayollar'),
        ('erkaklar','erkaklar'),
        ('kattalar','kattalar')
    )
    uid = models.BigIntegerField(db_index=True) #bor 
    name = models.CharField(max_length=255, null=True, blank=True) # bor 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,related_name='products') # bor 
    member  = models.ForeignKey(Member, on_delete= models.SET_NULL, null=True, blank=True)
    category_person = models.CharField(max_length=55, null=True, blank=True , choices=PERSON_CHOICES, default=None)
    producer = models.CharField(max_length=255, blank=True, null=True) # bor 
    country = models.CharField(max_length=255, blank=True, null=True) # bor 
    mnn = models.CharField(max_length=255, blank=True, null=True) # mor
    release_form = models.CharField(max_length=255, blank=True, null=True) # bor 
    product_type = models.CharField(max_length=255, blank=True, null=True) # bor  
    exp_date = models.CharField( max_length=155,blank=True, null=True)   # bor 
    ikpu = models.CharField(max_length=255, blank=True, null=True) # bor 
    package_code = models.CharField(max_length=255, blank=True, null=True) # bor 
    vat_percent = models.PositiveIntegerField(default=12)  # bor 
    inn = models.CharField(max_length=20, blank=True, null=True) #bor
    info = RichTextField(
        config_name='default',
        default='',
        blank=True,
        verbose_name='Mahsulot tavsifi'
    )
    image1 = models.ImageField(upload_to="images/", null=True, blank=True)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    def __str__(self):
        return str(self.uid)
    @property
    def image1_url(self):
        if self.image1:
            return f"https://akmalfarm.uz{self.image1.url}"
        return None

    
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_prise')
    price = models.PositiveIntegerField(default=0) # bor 
    amount = models.PositiveIntegerField( default=0) #bor 
    unique_identifier = models.CharField(max_length=255, unique=True, null=True, blank=True) # bor 

    def __str__(self):
        return f"{self.product.name}"
    
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
        ]
    
    @property
    def fiscal_items(self):

        vat_amount = (self.price / 1.12) * 0.12 if self.price > 0 else 0

        return {
            "Name": self.product.name,
            "SPIC": self.product.ikpu,
            "PackageCode": self.product.package_code,
            "Price": self.price * 100,  # tiyinlarda
            "Amount": self.amount,
            "VAT": vat_amount * 100,  # tiyinlarda
            "VATPercent": self.product.vat_percent,
            "CommissionInf": {
                "TIN": self.product.inn,
            },
        }


class Dostafca(models.Model):
    amount = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.amount}"


class Filial(models.Model):
    users = models.ManyToManyField(CustomUser, related_name='filials')
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Naqd'),
        ('card', 'Karta'),
        ('click', 'Click'),
    )
    TYPE_CHOICES = [
        ('Rad etilgan', 'Rad etilgan'),
        ('Kutilmoqda', 'Kutilmoqda'),
        ('Tasdiqlangan', 'Tasdiqlangan'),
        ('Topshirildi', 'Topshirildi '),
        
    ]
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True, related_name="finals")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='click')
    # Google Maps orqali yoki qo'lda kiritiladigan manzil
    address_text = models.CharField(max_length=255, blank=True, null=True)  # Qo'lda kiritish
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20 , null=True)
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=255, choices=TYPE_CHOICES, default='Kutilmoqda')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.first_name} - {self.filial.name if self.filial else 'No Filial'}"


    
    def complete_order(self):
        self.is_completed=True
        self.save()

    @property
    def total_price(self):
        """
        Hisobdagi barcha item'lar narxining yig'indisi va dostavka narxini qaytaradi
        """
        dostafca = Dostafca.objects.last()
        dostaff = dostafca.amount if dostafca and dostafca.amount else 0

        total = sum(item.total_price or 0 for item in self.items.all())
        return total + dostaff
    
    @property
    def status_color(self):
        return {
            'Rad etilgan': 'text-danger',
            'Kutilmoqda': 'text-warning',
            'Tasdiqlangan': 'text-primary',
            'Topshirildi': 'text-success',
        }.get(self.status, 'text-secondary')
    
    @property
    def amount(self):
        
        """For Click integration - returns the total price in UZS"""
        return self.total_price 


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default = 0)
    name = models.CharField(max_length=255,default='')

    def __str__(self):
        return f"Buyurtma {self.product.uid} {self.id} - {self.order} - {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity

     
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  

    def __str__(self):
        return f"{self.user.first_name} - {self.product.uid}"


class Aloqa(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=80)
    subject = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name



