from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    outlook_email = models.EmailField('Outlook email')
    secondary_password = models.CharField('Secondary password', max_length=50)
    latest_email_id = models.CharField('Latest email id', max_length=100, null=True, blank=True)