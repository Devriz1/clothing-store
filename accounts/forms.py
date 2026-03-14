from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['shipping_address']   # ✅ CORRECT
        labels = {
            'shipping_address': 'Default Shipping Address'
        }
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows':4})
        }