from .models import Order
from django import forms
from .models import *


class ContactForm(forms.ModelForm):
    class Meta:
        model = Aloqa
        fields = ["name", "email", "subject", "text"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ismingiz"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Emailingiz"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mavzu"}),
            "text": forms.Textarea(attrs={"class": "form-control", "placeholder": "Xabar yozing", "rows": 4}),
        }



class CheckoutForm(forms.ModelForm):
    filial = forms.ModelChoiceField(
        queryset=Filial.objects.all(), 
        empty_label="Filial tanlang", 
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        error_messages={
            'required': 'Iltimos, filial tanlang',
            'invalid_choice': 'Tanlangan filial mavjud emas'
        }
    )
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHODS, widget=forms.RadioSelect)
    address_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': "Manzilni qo'lda kiriting"}))
    phone_number1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Telefon raqamizi kiriting"}))
    phone_number2 = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': "qoshimcha raqamizi kiriting agar bolsa "}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always refresh the queryset to ensure it's up-to-date
        self.fields['filial'].queryset = Filial.objects.all()

    class Meta:
        model = Order
        fields = ['filial', 'payment_method', 'address_text','phone_number1','phone_number2']
