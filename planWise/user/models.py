from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    outlook_email = models.EmailField('Outlook 邮箱', unique=True)
    secondary_password = models.CharField('二级密码', max_length=50)