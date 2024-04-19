from django.db import models

from planWise.user.models import CustomUser

# Create your models here.
class Event(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(CustomUser)
    address = models.CharField(max_length=255)
    event = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)
    