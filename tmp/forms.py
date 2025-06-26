from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import AboutUs, Vacancy, OurPharmacie, Landlord, Public, Blog

class AboutUsForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = AboutUs
        fields = ['title', 'body', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sarlavhani kiriting: '}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control','placeholder': 'rasm hajmi 1 mbdan  oshmasin va 500x500 razmerda bo'lsin: '}),
        }
        labels = {
            'title': 'Yil',
            'body': 'Matn',
            'image': 'Rasm',
            'order': 'Tartib raqami'
        }
        help_texts = {
            'order': 'Kichikroq raqam yuqoriroq ko\'rsatiladi'
        } 
