
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django import forms
from .models import *


admin.site.register([Member,Category,Order,OrderItem,Filial,Dostafca, ProductPrice])
# admin.site.register(Category)

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