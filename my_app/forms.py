from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username','password1','password2','money']

class OrderForm(forms.Form):
    order_type = forms.ChoiceField(choices=[("buy","Buy"),("sell","Sell")])
    quantity = forms.IntegerField(min_value=1)