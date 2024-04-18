from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from mailhandler.emailProcessing.tool import Command as EmailCommand



@receiver(user_logged_in)
def sync_emails_on_login(sender, user, request, **kwargs):
    if "/admin/login/" in request.path:
        print("Admin login detected, skipping email sync.")
    else:
        # 实例化命令对象
        email_command = EmailCommand()
        # 调用 handle 方法，传入用户信息
        email_command.handle(user=user)

class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

class UserEditView(UpdateView):
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('login')
    template_name = 'registration/edit_profile.html'

# 登录和登出视图可以直接使用 Django 的内置视图
