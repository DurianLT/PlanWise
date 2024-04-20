from django.urls import path
from . import views

urlpatterns = [
    path('new_events/', views.CreateEventView.as_view(), name='new_events'),
    path('event_list/', views.CountdownView.as_view(), name='event_list'),
    path('event_detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit_event'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete_event'),
]