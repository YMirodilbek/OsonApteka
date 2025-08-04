from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from unicodedata import category
from .models import *


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['phone_number']
    search_fields = ("phone_number", "first_name", "last_name")
    ordering = ("phone_number",)

    # Barcha readonly (faqat ko‘rsatish, o‘zgartirib bo‘lmaydi) maydonlar
    readonly_fields = ("date_joined", "last_login")

    # Barcha maydonlarni ko‘rsatish
    fieldsets = (
        ("Login Info", {"fields": ("phone_number", "password")}),
        ("Personal Info", {
            "fields": (
                "first_name", "last_name", "telegram_id", "telegram_token", 
                "is_agree", "date_joined", "last_login","onesignal_player_id"
            )
        }),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_superuser", "is_active"),
        }),
    )

admin.site.register(PDFDocument)

admin.site.register(VirtualCard)
admin.site.register(EskizToken)
admin.site.register(Chat)

