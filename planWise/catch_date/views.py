from . import models
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import datetime
from django.views.generic import ListView
from django.utils.timezone import make_aware
from django.conf import settings
import pytz
from datetime import datetime


class CreateEventView(LoginRequiredMixin, CreateView):
    model = models.Event
    login_url = 'login'
    template_name = 'new_events.html'
    fields = ['date', 'address', 'event', 'comment', ]

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)


class EventListView(LoginRequiredMixin, ListView):
    model = models.Event
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # 获取当前用户的所有日程，并按日期排序
        return models.Event.objects.filter(user=self.request.user).order_by('date')


class EventDetailView(LoginRequiredMixin, DetailView):
    model = models.Event
    login_url = 'login'
    template_name = 'event_detail.html'
    fields = '__all__'


class CountdownView(ListView):
    model = models.Event
    template_name = 'events_countdown.html'
    context_object_name = 'events'

    def get_queryset(self):
        # 确保只获取当前用户的日程
        queryset = super().get_queryset().filter(user=self.request.user).order_by('date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = context['events']

        for event in events:
            if event.date:
                delta = event.date - timezone.now()
                if delta.total_seconds() < 0:
                    event.countdown = "已过期"
                elif delta.days > 0:
                    event.countdown = f"{delta.days} 天"
                elif delta.seconds >= 3600:  # 大于或等于1小时
                    hours = delta.seconds // 3600
                    event.countdown = f"{hours} 小时"
                else:
                    minutes = delta.seconds // 60
                    event.countdown = f"{minutes} 分钟"
            else:
                event.countdown = 'N/A'

        return context



