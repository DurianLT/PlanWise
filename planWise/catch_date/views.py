from . import models
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

# Create your views here.
class CreateEventView(LoginRequiredMixin, CreateView):
    model = models.Event
    login_url = 'login'
    template_name = 'new_events.html'
    fields = '__all__'

    def get_absolute_url(self):
        return reverse ('event_detail', args=[str(self.id)])

class EventListView(LoginRequiredMixin, ListView):
    model = models.Event
    login_url = 'login'        
    template_name = 'event_list.html'
    fields = '__all__'

class EventDetailView(LoginRequiredMixin, DetailView):
    model = models.Event
    login_url = 'login'
    template_name = 'event_detail.html'
    fields = '__all__'
