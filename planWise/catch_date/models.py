from django.db import models

from user.models import CustomUser

# Create your models here.
class Event(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    event = models.TextField()
    comment = models.CharField(max_length=255)
    