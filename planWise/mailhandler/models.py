from django.db import models

class Email(models.Model):
    subject = models.CharField(max_length=255)
    sender = models.EmailField()
    body = models.TextField()
    received_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
