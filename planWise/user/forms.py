from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'outlook_email', 'secondary_password')


class UserForm(forms.ModelForm):
    secondary_password = forms.CharField(widget=forms.PasswordInput(), label='Secondary Password')

    class Meta:
        model = CustomUser
        fields = ['outlook_email', 'secondary_password']
        widgets = {
            'outlook_email': forms.EmailInput(attrs={'placeholder': 'Enter your Outlook email'}),
        }