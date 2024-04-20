import json
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView
from mailhandler.emailProcessing.base import getMailsForIDs, getMailForID, analyze_email_content, select_best_result, \
    getNew10ID, loginTest
from user.forms import UserForm
from mailhandler.models import Email
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect, render

from .forms import EventForm
from .models import Email
from .emailProcessing.base import getNewID, getMailsForRange, fetch_and_process_emails, safe_loads, update_emails, \
    get_emails_from_db


class CheckUserView(LoginRequiredMixin, View):
    template_name = 'check_user.html'
    login_url = 'login'

    def get(self, request):
        user = request.user
        if not (user.outlook_email and user.secondary_password):
            return render(request, self.template_name, {'user': {'message': 'You have not bound your email address', 'updating': False}})

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            updated, emails = update_emails(user)
            if updated:
                return JsonResponse({'status': 'success', 'emails': emails})
            else:
                return JsonResponse({'status': 'no_update'})

        user_info = {
            'outlook_email': user.outlook_email,
            'secondary_password': '**********',
            'message': 'You have bound your email address',
            'updating': True,
            'emails': get_emails_from_db(user)
        }
        return render(request, self.template_name, {'user': user_info})


class UpdateUserView(LoginRequiredMixin, View):
    template_name = 'update_emails.html'
    login_url = 'login'

    def get(self, request):
        user = request.user
        form = UserForm(instance=user)
        return render(request, self.template_name, {'form': form, 'user': user})

    def post(self, request):
        user = request.user
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            if loginTest(user.outlook_email, user.secondary_password):
                form.save()
                fetch_and_process_emails(user)
                return JsonResponse({'status': 'success', 'message': 'Credentials valid and emails saved.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})
        return JsonResponse({'status': 'error', 'message': 'Form is invalid'})


class EmailDetailView(DetailView):
    model = Email
    context_object_name = 'email_data'
    template_name = 'email_detail.html'

    def get_queryset(self):
        # 这里过滤只允许用户查看自己的邮件
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        email = context['email_data']

        # 判断并解析事件详情
        event_details = safe_loads(email.event_details) if email.event_details != 'None' else None

        # 根据事件详情初始化表单
        if event_details:
            if 'time' in event_details and event_details['time'] is not None and event_details['time'] != 'null':
                if 'date' in event_details and event_details['date'] is not None and event_details['date'] != 'null':
                    datetime_str = f"{event_details['date']} {event_details['time']}"
                else:
                    datetime_str = f"{datetime.datetime.now().date()} {event_details['time']}"
                    # 如果只提供了日期而没有提供时间，则默认将时间设置为"00:00:00"
            elif 'date' in event_details and event_details['date'] is not None and event_details['date'] != 'null':
                datetime_str = f"{event_details['date']} 00:00:00"
                # 如果既没有提供日期也没有提供时间，则使用当前日期和时间
            else:
                datetime_str = f"{datetime.datetime.now().date()} 00:00:00"

            datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

            initial_data = {
                'date': datetime_obj,  # 使用 datetime 对象
                'address': event_details.get('place', ''),
                'event': event_details.get('events', ''),
                'comment': ''
            }
        else:
            initial_data = {
                'date': datetime.datetime.now().date(),
                'address': '',
                'event': '',
                'comment': ''
            }

        # 使用初始化数据创建表单
        context['event_form'] = EventForm(initial=initial_data)

        return context


class EmailEventCreateView(FormView):
    template_name = 'email_event_create.html'
    form_class = EventForm
    success_url = reverse_lazy('check-users')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)
