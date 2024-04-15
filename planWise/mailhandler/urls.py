from django.urls import path
from . import views

urlpatterns = [
    path('emails/', views.EmailListView.as_view(), name='email-list'),
    path('emails/<int:pk>/', views.EmailDetailView.as_view(), name='email-detail'), 
    path('calendar/', views.CalendarView.as_view(), name='calendar-view'),
]