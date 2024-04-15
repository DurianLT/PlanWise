import calendar
from datetime import datetime
import json
from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import Email
from django.utils.safestring import mark_safe
from django.views import View

# Create your views here.
class EmailListView(ListView):
    model = Email
    template_name = 'events_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 为每个对象添加解析过的 JSON 数据
        for email in context['object_list']:
            email.analysis_data = email.get_analysis_data()
        return context
    
class EmailDetailView(DetailView):
    model = Email
    template_name = 'email_detail.html'  # 指定用于详情页面的模板

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加解析的 JSON 数据
        context['analysis_data'] = context['object'].get_analysis_data()
        return context
    
from django.http import HttpResponse
import json
import calendar
from datetime import datetime
from django.shortcuts import render
from .models import Email  # 确保这是正确的路径

class CalendarView(View):
    def get(self, request, year=datetime.now().year, month=datetime.now().month):
        # 初始化日历
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.itermonthdays(year, month)
        # 获取该月的所有邮件
        emails = Email.objects.filter(received_at__year=year, received_at__month=month)
        # 解析所有邮件的事件并按日期整理
        events_by_date = {}

        for email in emails:
            # 添加异常处理以避免 JSON 解析错误
            try:
                data = json.loads(email.analysis) if email.analysis else {}
            except json.JSONDecodeError:
                print(f"解析错误: {email.analysis}")
                data = {}

            date = data.get('date')
            if date:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                if date_obj in events_by_date:
                    events_by_date[date_obj].append(data)
                else:
                    events_by_date[date_obj] = [data]

        # 创建日历网格
        weeks = []
        week = []
        for day in month_days:
            if day != 0:
                date_obj = datetime(year, month, day).date()
                events = events_by_date.get(date_obj, [])
            else:
                events = []
            week.append((day, events))
            if len(week) == 7:
                weeks.append(week)
                week = []
        if week:
            weeks.append(week)

        context = {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'weeks': weeks,
        }
        return render(request, 'calendar.html', context)