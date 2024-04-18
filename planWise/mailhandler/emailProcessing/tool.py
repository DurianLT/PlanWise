import requests
import json
from django.utils.timezone import now
from email.utils import parseaddr
import html
import re
from django.core.management.base import BaseCommand
from mailhandler.models import Email
import imaplib
import email
from email.header import decode_header, make_header
from bs4 import BeautifulSoup  # type: ignore
from user.models import CustomUser
import imaplib


def clean_text(text):
    """清理邮件正文中的多余空格并保留换行"""
    # 只移除行内的多余空格，不影响换行符
    lines = text.splitlines()
    cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in lines]
    # 使用html.unescape处理HTML实体
    cleaned_text = html.unescape('\n'.join(cleaned_lines))
    return cleaned_text


# 登陆邮箱并读取原始邮件
def get_mail(email_address, password):
    try:
        # 选择服务器
        server = imaplib.IMAP4_SSL('outlook.office365.com')
        server.login(email_address, password)
        server.select("INBOX")
        # 搜索匹配的邮件
        email_type, data = server.search(None, "UNSEEN")
        # 邮件列表，使用空格分割得到邮件索引
        msglist = data[0].split()

        print('未读邮件一共有：', len(msglist))  # 显示未读邮件数量

        emails = []
        for msg_num in msglist:
            email_type, datas = server.fetch(msg_num, '(RFC822)')

            try:
                text = datas[0][1].decode('utf-8', errors='ignore')
                message = email.message_from_bytes(datas[0][1])
                message_id = message.get('Message-ID').strip()  # 获取邮件的 Message-ID
                emails.append((message, message_id))
            except UnicodeDecodeError as e:
                print("UnicodeDecodeError occurred. Skipping this email.")

        server.logout()
        return emails
    except imaplib.IMAP4.error as e:
        print("登录失败:", e)
        return []


def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            charset = guess_charset(part)

            if content_type == "text/plain" and "attachment" not in content_disposition:
                text = part.get_payload(decode=True).decode(charset if charset else 'utf-8', 'ignore')
                cleaned_text = clean_text(text)  # 清理文本
                return cleaned_text
            elif content_type == "text/html" and "attachment" not in content_disposition:
                html_content = part.get_payload(decode=True).decode(charset if charset else 'utf-8', 'ignore')
                soup = BeautifulSoup(html_content, "lxml")
                text = soup.get_text()
                cleaned_text = clean_text(text)  # 清理文本
                return cleaned_text
    else:
        content_type = msg.get_content_type()
        charset = guess_charset(msg)
        if content_type == "text/html":
            html_content = msg.get_payload(decode=True).decode(charset if charset else 'utf-8', 'ignore')
            soup = BeautifulSoup(html_content, "lxml")
            text = soup.get_text()
            cleaned_text = clean_text(text)  # 清理文本
            return cleaned_text
        text = msg.get_payload(decode=True).decode(charset if charset else 'utf-8', 'ignore')
        cleaned_text = clean_text(text)  # 清理文本
        return cleaned_text


# 将原始邮件转化为可读邮件
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return str(make_header(decode_header(s)))


# 检测邮件编码函数
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


# 通过循环遍历来读取邮件内容
def print_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))

    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


def analyze_email_content(email_content):
    url = "http://154.44.10.169:1145/analyze_email"
    data = {"email_content": email_content}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get a successful response from the API. Status Code:", response.status_code)
        return None


def select_best_result(results):
    best_score = 0
    best_result = None

    for result in results:
        # 检查结果类型，如果不是字典则尝试解析为字典
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                continue  # 如果字符串不是有效的JSON，跳过这个结果
        elif not isinstance(result, dict):
            continue  # 如果结果既不是字符串也不是字典，跳过

        score = 0
        if result.get('date'):
            score += 10
        if result.get('time'):
            score += 5
        if result.get('events') and result.get('isEvents') == 'True':
            score += 10
        if result.get('place'):
            score += 5

        if score > best_score:
            best_score = score
            best_result = result

    return best_result



class Command(BaseCommand):
    help = 'Receive emails from Outlook and analyze them'

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        for user in users:
            self.stdout.write(self.style.SUCCESS(f'Fetching emails for {user.username}'))
            emails = get_mail(user.outlook_email, user.secondary_password)

            for messageObject, message_id in emails:
                if messageObject and message_id:
                    subject = decode_str(messageObject["Subject"])
                    from_ = decode_str(messageObject["From"])
                    date_ = email.utils.parsedate_to_datetime(messageObject["Date"])
                    body = get_email_body(messageObject)

                    print("id:\n%s" % message_id)
                    print("主题: %s" % subject)
                    print("发件人: %s" % from_)
                    print("发送时间: %s" % date_)
                    print("正文:\n%s" % body)

                    # 检查数据库中是否已经存储了这封邮件
                    try:
                        existing_email = Email.objects.get(message_id=message_id)
                        print("这封邮件已经接收并存储过了。")
                    except Email.DoesNotExist:
                        # 调用 API 分析邮件内容
                        results = [analyze_email_content(body) for _ in range(3)]
                        best_result = select_best_result(results)
                        print("最佳分析结果:", best_result)

                        # 保存邮件到数据库
                        Email.objects.create(
                            user=user,
                            subject=subject,
                            sender=from_,
                            body=body,
                            analysis=json.dumps(best_result),
                            received_at=date_ or now(),
                            message_id=message_id
                        )
                        print("邮件已保存到数据库。")
                else:
                    print("没有新邮件或未能获取邮件ID。")