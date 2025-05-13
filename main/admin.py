from unicodedata import category

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        # Telefon raqamni tozalash va +998 formatiga moslash
        cleaned_number = ''.join(filter(str.isdigit, obj.phone_number))
        if cleaned_number.startswith('998') and len(cleaned_number) == 12:
            obj.phone_number = f"+{cleaned_number}"
        super().save_model(request, obj, form, change)

    model = CustomUser
    list_display = ("phone_number", "first_name", "last_name", "is_agree", "is_staff", "is_superuser", "is_active")
    search_fields = ("phone_number", "first_name", "last_name")
    ordering = ("phone_number",)  # Telefon raqam bo‘yicha tartiblash

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Other Info", {"fields": ("is_agree",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PDFDocument)
admin.site.register(EskizToken)

#Product

