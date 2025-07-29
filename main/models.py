from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from random import randint
import uuid
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish"""
        if not phone_number:
            raise ValueError("Telefon raqam kiritilishi shart")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Superuser yaratish"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=13, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False)  
    is_agree = models.BooleanField(default=False) 
    date_joined = models.DateTimeField(auto_now_add=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    telegram_token = models.CharField(max_length=100, unique=True, null=True, blank=True, default=uuid.uuid4)
    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number
    @property
    def user_cart_items(self):
        from Product.models import OrderItem  
        return OrderItem.objects.filter(order__user=self, order__is_completed=False).count()


class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.title


class EskizToken(models.Model):
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class Chat(models.Model):
    room_id = models.PositiveIntegerField()# client user id 
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
    blank=True, related_name='chats')
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    voice = models.FileField(upload_to='chat_voices/', blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    
class VirtualCard(models.Model):
    
    CARD_STATUS = (
        ('ACTIVE', 'Faol'),
        ('BLOCKED', 'Bloklangan'),
        ('EXPIRED', 'Muddati o\'tgan'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='virtual_cards')
    card_number = models.CharField(max_length=16, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cvv = models.CharField(max_length=3, editable=False)
    status = models.CharField(max_length=10, choices=CARD_STATUS, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Virtual Karta'
        verbose_name_plural = 'Virtual Kartalar'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.card_type} - {self.masked_card_number}"

    @property
    def masked_card_number(self):
        return f"**** **** **** {self.card_number[-4:]}" if self.card_number else ""
    
    @staticmethod
    def generate_card_number():
        """Karta raqamini generatsiya qilish"""

        return ''.join([str(randint(0, 9)) for _ in range(16)])

    @staticmethod
    def generate_cvv():   
        return ''.join([str(randint(0, 9)) for _ in range(3)])
    
    def save(self, *args, **kwargs):
        # Yangi karta yaratilayotganda
        if not self.card_number:
            self.card_number = self.generate_card_number()
            self.cvv = self.generate_cvv()
        super().save(*args, **kwargs)