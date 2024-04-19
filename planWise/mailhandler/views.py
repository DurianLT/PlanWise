import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.views.generic import DetailView

from mailhandler.emailProcessing.base import getMailsForIDs, getMailForID

from mailhandler.emailProcessing.tool import analyze_email_content, select_best_result

from user.forms import UserForm

from mailhandler.emailProcessing.base import getNew10ID

from mailhandler.emailProcessing.base import loginTest

from mailhandler.models import Email

from user.models import CustomUser

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .models import Email
from .emailProcessing.base import getNew10ID, getMailsForIDs, getNewID, getMailsForRange


def safe_loads(json_string):
    # 尝试用标准的双引号 JSON 解析
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        # 如果标准解析失败，尝试修复常见的问题
        try:
            # 替换单引号为双引号，并将None转换为null
            corrected_json_string = json_string.replace("'", '"').replace("None", "null")
            return json.loads(corrected_json_string)
        except json.JSONDecodeError as e:
            print("JSON 解析失败:", e)
            return None  # 或返回适当的默认值或错误信息


class CheckUserView(LoginRequiredMixin, View):
    template_name = 'check_user.html'
    login_url = 'login'

    def get(self, request):
        user = request.user
        if not (user.outlook_email and user.secondary_password):
            return render(request, self.template_name, {'user': {'message': '你未绑定邮箱', 'updating': False}})

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response = self.update_emails(user)
            return response

        user_info = {
            'outlook_email': user.outlook_email,
            'secondary_password': '**********',
            'message': '你已绑定邮箱',
            'updating': True,
            'emails': self.get_emails_from_db(user)
        }
        return render(request, self.template_name, {'user': user_info})

    def get_emails_from_db(self, user):
        emails = Email.objects.filter(user=user).order_by('-date')
        prepared_emails = []
        for email in emails:
            # 使用 safe_loads 安全解析 event_details 字符串
            if email.event_details != 'None':
                event_details = safe_loads(email.event_details)
            else:
                event_details = email.event_details

            prepared_emails.append({
                'pk': email.pk,
                'from_email': email.from_email,
                'subject': email.subject,
                'date': email.date,
                'body': email.body,
                'message_id': email.message_id,
                'event_details': event_details
            })
        return prepared_emails

    def update_emails(self, user):
        latest_mail_id = getNewID(user.outlook_email, user.secondary_password)
        if int(user.latest_email_id) != int(latest_mail_id):
            new_emails = getMailsForRange(user.outlook_email, user.secondary_password, int(user.latest_email_id),
                                          int(latest_mail_id))
            latest_email_id = None
            for email in new_emails:
                body = email[3]
                # 解析邮件内容
                results = [analyze_email_content(body) for _ in range(3)]
                best_result = select_best_result(results)
                event_details = self.parse_best_result(best_result)  # 假设这个方法定义了如何解析和格式化结果

                # 更新或创建邮件记录，同时保存事件详情
                obj, created = Email.objects.update_or_create(
                    user=user,
                    message_id=email[4],
                    defaults={
                        'from_email': email[0],
                        'subject': email[1],
                        'date': email[2],
                        'body': body,
                        'event_details': event_details  # 保存解析的事件详情
                    }
                )
                if not latest_email_id or email[4] > latest_email_id:
                    latest_email_id = email[4]

            if latest_email_id:
                user.latest_email_id = latest_email_id
                user.save(update_fields=['latest_email_id'])

            emails = self.get_emails_from_db(user)
            return JsonResponse({'status': 'success', 'emails': emails})

        return JsonResponse({'status': 'no_update'})

    def parse_best_result(self, result):
        # 逻辑来格式化结果字符串
        return f"{result}"


class UpdateUserView(LoginRequiredMixin, View):
    template_name = 'update_emails.html'
    login_url = 'login'

    def get(self, request):
        user = request.user
        form = UserForm(instance=user)  # 创建表单实例，使用当前用户的数据填充
        return render(request, self.template_name, {'form': form, 'user': user})

    def post(self, request):
        user = request.user
        form = UserForm(request.POST, instance=user)  # 绑定表单到当前用户
        if form.is_valid():
            if loginTest(user.outlook_email, user.secondary_password):
                form.save()  # 保存用户信息
                latest_ids = getNew10ID(user.outlook_email, user.secondary_password)
                emails = getMailsForIDs(user.outlook_email, user.secondary_password, latest_ids)
                latest_email_id = None
                for email in emails:
                    from_email, subject, date, body, msg_id = email
                    # 进行邮件内容解析
                    results = [analyze_email_content(body) for _ in range(3)]
                    best_result = select_best_result(results)
                    event_details = self.parse_best_result(best_result)
                    # 更新或创建邮件记录，同时保存事件详情
                    obj, created = Email.objects.update_or_create(
                        user=user,
                        message_id=msg_id,
                        defaults={'from_email': from_email, 'subject': subject, 'date': date, 'body': body,
                                  'event_details': event_details}
                    )
                    if not latest_email_id or msg_id > latest_email_id:
                        latest_email_id = msg_id  # 更新最新邮件ID

                if latest_email_id:
                    user.latest_email_id = latest_email_id
                    user.save(update_fields=['latest_email_id'])  # 保存最新邮件ID到用户模型

                return JsonResponse({'status': 'success', 'message': 'Credentials valid and emails saved.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})
        return JsonResponse({'status': 'error', 'message': 'Form is invalid'})

    def parse_best_result(self, result):
        # 逻辑来格式化结果字符串
        return f"{result}"


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
        if email.event_details != 'None':
            event_details = safe_loads(email.event_details)
        else:
            event_details = email.event_details
        context['email_data'].event_details = event_details
        return context


class DisplayEmailsView(LoginRequiredMixin, View):
    template_name = 'display_emails.html'
    login_url = 'login'

    def get(self, request):
        # 只负责渲染基础页面
        return render(request, self.template_name)


class GetEmailsView(View):
    def get(self, request, user_id):
        user = CustomUser.objects.get(pk=user_id)
        userName = user.outlook_email
        password = user.secondary_password
        ids = [4172, 4173, 4174, 4175, 4178, 4177]  # 示例 ID
        emails = getMailsForIDs(userName, password, ids)  # 获取邮件数据
        return JsonResponse({'emails': emails})  # 返回JSON响应


class DisplayEmailView(LoginRequiredMixin, View):
    template_name = 'display_email.html'
    login_url = 'login'

    def get(self, request):
        email_info_list = []
        users = CustomUser.objects.all()

        for user in users:
            userName = user.outlook_email
            password = user.secondary_password
            specific_msg_id = 4225  # 根据需要调整

            if userName and password:
                email_data = getMailForID(userName, password, specific_msg_id)
                if isinstance(email_data, str):
                    continue  # 跳过错误消息

                from_decoded = email_data[0][0]
                subject = email_data[0][1]
                date = email_data[0][2]
                body = email_data[0][3]

                results = [analyze_email_content(body) for _ in range(3)]
                best_result = select_best_result(results)

                event_details = self.parse_best_result(best_result)

                email_info_list.append({
                    'from': from_decoded,
                    'subject': subject,
                    'date': date,
                    'body': body,
                    'event_details': event_details
                })

        return render(request, self.template_name, {'emails': email_info_list})

    def parse_best_result(self, best_result):
        if best_result.get('isEvents') == 'True':
            details = '帮你解析到了事件：'
            if best_result.get('date'):
                details += f"日期：{best_result['date']} "
            if best_result.get('time'):
                details += f"时间：{best_result['time']} "
            if best_result.get('place'):
                details += f"地点：{best_result['place']} "
            if best_result.get('events'):
                details += f"事件：{best_result['events']} "
            return details
        else:
            return '没有解析出事件'
