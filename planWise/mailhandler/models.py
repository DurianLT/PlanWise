import json
from django.conf import settings
from django.db import models


class Email(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emails')
    message_id = models.CharField(max_length=255, unique=True)
    from_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    date = models.DateTimeField()
    body = models.TextField()
    event_details = models.TextField(blank=True, null=True)  # 用于存储日程解析结果

    class Meta:
        unique_together = ('user', 'message_id')  # 同一用户不会有重复的邮件ID
