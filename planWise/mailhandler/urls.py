# 在你的 urls.py 文件中
from django.urls import path
from .views import CheckUserView, DisplayEmailsView, DisplayEmailView, GetEmailsView, UpdateUserView

urlpatterns = [
    path('check-users/', CheckUserView.as_view(), name='check-users'),
    path('display-emails/', DisplayEmailsView.as_view(), name='display-emails'),
    path('get-emails/<int:user_id>/', GetEmailsView.as_view(), name='get-emails'),
    path('display-email/', DisplayEmailView.as_view(), name='display-email'),
    path('update-email/', UpdateUserView.as_view(), name='update-email'),
]
