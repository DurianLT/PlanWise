from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView

from . import models
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

# 登录和登出视图可以直接使用 Django 的内置视图
