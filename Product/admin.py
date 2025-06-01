from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([Category,Order,OrderItem,Filial,Dostafca])

from ckeditor.widgets import CKEditorWidget
from django import forms

class ProductAdminForm(forms.ModelForm):
    info = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Product
        fields = '__all__'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('uid', 'created_at')
    search_fields = ('uid', 'info')