# 在你的 urls.py 文件中
from django.urls import path
from .views import CheckUserView, UpdateUserView, EmailDetailView, EmailEventCreateView

urlpatterns = [
    path('check-users/', CheckUserView.as_view(), name='check-users'),
    path('update-email/', UpdateUserView.as_view(), name='update-email'),
    path('email/<int:pk>/', EmailDetailView.as_view(), name='email_detail'),
    path('submit-event/', EmailEventCreateView.as_view(), name='submit_event'),
]
