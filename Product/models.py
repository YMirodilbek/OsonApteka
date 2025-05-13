from django.contrib.auth import get_user_model
from django.utils.timezone import now
from main.models import CustomUser
from django.db import models
from main.models import *

User = get_user_model()
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Product(models.Model):
    uid = models.BigIntegerField(db_index=True)
    # category = models.ManyToManyField(Category, related_name="products")
    info = models.TextField(default='', blank=True)
    # new_price = models.FloatField(null=True, blank=True)
    # price = models.FloatField()
    # rate = models.FloatField(null=True, blank=True)
    # text = models.TextField()
    image1 = models.ImageField(upload_to="images/", null=True, blank=True)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.uid)



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
        (1, 'Rad etilgan'),
        (2, 'Kutilmoqda'),
        (3, 'Tasdiqlangan'),
        (4, 'Topshirildi '),
        
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
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
    status = models.IntegerField( choices=TYPE_CHOICES, default=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.first_name} - {self.filial.name if self.filial else 'No Filial'}"


    
    def complete_order(self):
        self.is_completed=True
        self.save()

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    
    @property
    def status_color(self):
        return {
            1: 'text-danger',
            2: 'text-warning',
            3: 'text-primary',
            4: 'text-success',
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



