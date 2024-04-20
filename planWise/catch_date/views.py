from . import models
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView,UpdateView,DeleteView
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
    
class EventUpdateView(UpdateView):
    model = models.Event
    fields = ['date', 'event', 'address', 'comment']
    template_name = 'edit_event.html'

    def get_success_url(self):
        return reverse_lazy('event_list')  # 假设你有一个显示所有事件的视图
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class EventDeleteView(DeleteView):
    model = models.Event
    template_name = 'delete_event.html'
    success_url = reverse_lazy('event_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)  # 仅允许用户删除自己的事件

class EventDetailView(LoginRequiredMixin, DetailView):
    model = models.Event
    login_url = 'login'
    template_name = 'event_detail.html'
    fields = '__all__'

class CountdownView(ListView):
    model = models.Event
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # 获取排序参数
        sort = self.request.GET.get('sort', 'date')  # 默认按日期排序
        # 确保只获取当前用户的日程
        if sort == 'countdown':
            # 如果排序依据是倒计时，这里需要一种方法来排序，可能需要额外的逻辑
            queryset = super().get_queryset().filter(user=self.request.user)
            queryset = sorted(queryset, key=lambda x: (x.date - timezone.now()).total_seconds())
        else:
            # 默认按日期排序
            queryset = super().get_queryset().filter(user=self.request.user).order_by('date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = context['events']

        for event in events:
            if event.date:
                delta = event.date - timezone.now()
                if delta.total_seconds() < 0:
                    event.countdown = "Expired"
                elif delta.days > 0:
                    event.countdown = f"{delta.days} days"
                elif delta.seconds >= 3600:  # 大于或等于1小时
                    hours = delta.seconds // 3600
                    event.countdown = f"{hours} hours"
                else:
                    minutes = delta.seconds // 60
                    event.countdown = f"{minutes} minutes"
            else:
                event.countdown = 'N/A'

        return context



