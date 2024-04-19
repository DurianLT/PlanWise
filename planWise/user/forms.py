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
    secondary_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password-input', 'placeholder': 'Enter your secondary password'}), label='Secondary Password')

    class Meta:
        model = CustomUser
        fields = ['outlook_email', 'secondary_password']
        widgets = {
            'outlook_email': forms.EmailInput(attrs={'placeholder': 'Enter your Outlook email'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.outlook_email:
            self.fields['outlook_email'].widget = forms.TextInput(attrs={'readonly': True, 'value': self.instance.outlook_email})
