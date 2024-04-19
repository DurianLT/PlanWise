from django.urls import path
from . import views
from .views import CountdownView

urlpatterns = [
    path('new_events/', views.CreateEventView.as_view(), name='new_events'),
    path('event_list/', views.EventListView.as_view(), name='event_list'),
    path('event_detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event-countdown/', CountdownView.as_view(), name='event_countdown'),
]