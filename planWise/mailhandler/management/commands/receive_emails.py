from email.utils import parseaddr
import html
import re
from django.core.management.base import BaseCommand
from mailhandler.models import Email
import imaplib
import email
from email.header import decode_header, make_header
from bs4 import BeautifulSoup # type: ignore

email_address = 'liutianjunrong@outlook.com'
password = 'qyzbnfwusynxjqvh'

def clean_text(text):
    """清理邮件正文中的多余空格和HTML实体"""
    # 使用正则表达式移除多于的空格
    text = re.sub(r'\s+', ' ', text)
    # 使用html.unescape处理HTML实体
    text = html.unescape(text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# 登陆邮箱并读取原始邮件
def get_mail(email_address, passsword):
    # 选择服务器
    server = imaplib.IMAP4_SSL('outlook.office365.com')
    server.login(email_address, passsword)
    server.select("INBOX")
    # 搜索匹配的邮件
    email_type, data = server.search(None, "UNSEEN")
    # 邮件列表，使用空格分割得到邮件索引
    msglist = data[0].split()

    print('未读邮件一共有：', len(msglist))  # 显示未读邮件数量
    
    if len(msglist) != 0:
        # 处理最新的未读邮件
        latest = msglist[-1]  # 获取最新一封未读邮件的ID
        email_type, datas = server.fetch(latest, '(RFC822)')
        text = datas[0][1].decode('utf-8')
        message = email.message_from_bytes(datas[0][1])  # 使用message_from_bytes代替message_from_string
        return message
    else:
        print("暂无未读邮件")
        return None

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

#检测邮件编码函数
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type','').lower()
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


class Command(BaseCommand):
    help = 'Receive emails from Outlook'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Successfully called command'))
        messageObject = get_mail(email_address, password)
        if messageObject:
            # 使用 decode_str 解码邮件主题和发件人信息
            subject = decode_str(messageObject["Subject"])
            from_ = decode_str(messageObject["From"])
            date_ = email.utils.parsedate_to_datetime(messageObject["Date"])
            body = get_email_body(messageObject)
            
            print("主题: %s" % subject)
            print("发件人: %s" % from_)
            print("发送时间: %s" % date_)
            print("正文:\n%s" % body)

            # 可以在这里保存邮件到数据库
            # Email.objects.create(subject=subject, sender=from_, body=body)