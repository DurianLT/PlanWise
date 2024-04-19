from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    outlook_email = models.EmailField('Outlook 邮箱')
    secondary_password = models.CharField('二级密码', max_length=50)
    latest_email_id = models.CharField('最新邮件ID', max_length=100, null=True, blank=True)