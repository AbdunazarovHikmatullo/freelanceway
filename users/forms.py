from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm 


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar', 'is_freelancer', 'is_employer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_freelancer'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_employer'].widget.attrs.update({'class': 'form-check-input'})
