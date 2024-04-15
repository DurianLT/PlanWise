import json
from django.conf import settings
from django.db import models



class Email(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emails')
    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    body = models.TextField()
    analysis = models.TextField()  # 存储分析结果的JSON字符串
    received_at = models.DateTimeField()  # 邮件接收时间
    message_id = models.CharField(max_length=255, unique=True)  # 用于唯一识别每封邮件

    def __str__(self):
        return self.subject
    
    def get_analysis_data(self):
        return json.loads(self.analysis)

