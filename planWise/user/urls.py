from django.urls import path
from .views import UserRegisterView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]