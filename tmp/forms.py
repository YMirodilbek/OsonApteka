from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import AboutUs, Vacancy, OurPharmacie, Landlord, Public, Blog

class AboutUsForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = AboutUs
        fields = ['title', 'body', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sarlavhani kriitng: '}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
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
