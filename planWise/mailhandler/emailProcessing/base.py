import json
import re

from bs4 import BeautifulSoup
import requests
from imapclient import IMAPClient
from email.header import decode_header
from email import message_from_bytes
import ssl
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from mailhandler.models import Email


def clean_text(html_content):
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'lxml')

    # 获取所有文本内容，去除标签
    text = soup.get_text(separator='\n')  # 使用换行符作为分隔符

    # 分割文本为行，并清洗每一行
    lines = text.splitlines()
    cleaned_text = '\n'.join(
        [re.sub(r'\s+', ' ', line).strip() for line in lines if line.strip()])  # 清除行内多余的空格，并连接为一个字符串

    return cleaned_text


def getMailHostPort(userName):
    if 'gmail.com' in userName:
        host = 'imap.gmail.com'
        port = 993
    elif 'outlook.com' in userName:
        host = 'outlook.office365.com'
        port = 993
    else:
        host = 'imap.gmail.com'
        port = 993

    return host, port


def parse_email(data):
    envelope = data[b'ENVELOPE']
    email_message = message_from_bytes(data[b'RFC822'])

    # 解码发件人信息
    from_ = envelope.from_[0]
    from_decoded = "{}@{}".format(from_.mailbox.decode(), from_.host.decode())

    # 解码主题
    subject_encoded = envelope.subject
    subject = ''
    if isinstance(subject_encoded, bytes):
        subject_encoded = subject_encoded.decode('utf-8', errors='replace')
    subject_decoded = decode_header(subject_encoded)
    for part, encoding in subject_decoded:
        if encoding:
            subject += part.decode(encoding, errors='replace')
        else:
            subject += part if isinstance(part, str) else part.decode('utf-8', errors='replace')

    # 提取邮件正文
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                text = part.get_payload(decode=True).decode(part.get_content_charset(), 'replace')
                body = clean_text(text)
                break
    else:
        text = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), 'replace')
        body = clean_text(text)

    # 处理时间
    utc_date = datetime.fromtimestamp(envelope.date.timestamp(), timezone.utc)
    beijing_date = utc_date.astimezone(ZoneInfo("Asia/Shanghai"))

    return from_decoded, subject, beijing_date, body


def loginTest(userName, password):
    host, port = getMailHostPort(userName)

    # 使用SSL连接
    context = ssl.create_default_context()

    try:
        with IMAPClient(host, port=port, ssl_context=context) as client:
            # 尝试登录
            client.login(userName, password)
            return True
    except Exception as e:
        return False


def getMailForID(userName, password, specific_msg_id):
    host, port = getMailHostPort(userName)
    context = ssl.create_default_context()

    with IMAPClient(host, port=port, ssl_context=context) as client:
        client.login(userName, password)
        client.select_folder('INBOX', readonly=True)

        results = []
        try:
            data = client.fetch([specific_msg_id], ['ENVELOPE', 'RFC822'])
            if specific_msg_id not in data:
                return "ID not found"

            from_decoded, subject, date, body = parse_email(data[specific_msg_id])
            results.append((from_decoded, subject, date, body, specific_msg_id))
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return 'error'
        finally:
            client.logout()

        return results


def getMailsForRange(userName, password, id_start, id_end):
    host, port = getMailHostPort(userName)
    context = ssl.create_default_context()

    with IMAPClient(host, port=port, ssl_context=context) as client:
        client.login(userName, password)
        client.select_folder('INBOX', readonly=True)

        results = []

        for msg_id in range(id_start, id_end + 1):
            try:
                data = client.fetch([msg_id], ['ENVELOPE', 'RFC822'])
                if msg_id not in data:
                    continue  # 如果邮件ID不存在，则跳过

                from_decoded, subject, date, body = parse_email(data[msg_id])
                results.append((from_decoded, subject, date, body, msg_id))
            except Exception as e:
                print(f"Error fetching mail ID {msg_id}: {str(e)}")

        client.logout()

        return results


def getMailsForIDs(userName, password, ids):
    host, port = getMailHostPort(userName)
    context = ssl.create_default_context()

    with IMAPClient(host, port=port, ssl_context=context) as client:
        client.login(userName, password)
        client.select_folder('INBOX', readonly=True)

        results = []

        for msg_id in ids:
            try:
                data = client.fetch([msg_id], ['ENVELOPE', 'RFC822'])
                if msg_id not in data:
                    continue  # 如果邮件ID不存在，则跳过

                from_decoded, subject, date, body = parse_email(data[msg_id])
                results.append((from_decoded, subject, date, body, msg_id))
            except Exception as e:
                print(f"Error fetching mail ID {msg_id}: {str(e)}")

        client.logout()

        return results


def getNewID(userName, password):
    host, port = getMailHostPort(userName)

    # 使用SSL连接
    context = ssl.create_default_context()

    with IMAPClient(host, port=port, ssl_context=context) as client:
        # 登录
        client.login(userName, password)

        # 选择邮箱，使用readonly模式以防止意外地修改任何邮件
        client.select_folder('INBOX', readonly=True)

        # 获取所有邮件的ID
        messages = client.search('ALL')

        # 获取最新一封邮件的ID
        latest_email_id = messages[-1] if messages else None

        client.logout()

    return latest_email_id


def getNew10ID(userName, password):
    host, port = getMailHostPort(userName)

    # 使用SSL连接
    context = ssl.create_default_context()

    with IMAPClient(host, port=port, ssl_context=context) as client:
        # 登录
        client.login(userName, password)

        # 选择邮箱，使用readonly模式以防止意外地修改任何邮件
        client.select_folder('INBOX', readonly=True)

        # 获取所有邮件的ID
        messages = client.search('ALL')

        # 获取最新的十封邮件的ID
        if len(messages) > 10:
            latest_emails_ids = messages[-10:]
        else:
            latest_emails_ids = messages

        # 注销
        client.logout()

    return latest_emails_ids


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


def fetch_and_process_emails(user):
    if user.latest_email_id is None:
        latest_ids = getNew10ID(user.outlook_email, user.secondary_password)
        emails = getMailsForIDs(user.outlook_email, user.secondary_password, latest_ids)
        latest_email_id = None
        for email in emails:
            latest_email_id = process_email(user, email, latest_email_id)
        if latest_email_id:
            user.latest_email_id = latest_email_id
            user.save(update_fields=['latest_email_id'])
    else:
        latest_email_id = getNewID(user.outlook_email, user.secondary_password)
        if int(user.latest_email_id) != int(latest_email_id):
            emails = getMailsForRange(user.outlook_email, user.secondary_password, int(user.latest_email_id),
                                          int(latest_email_id))
            for email in emails:
                latest_email_id = process_email(user, email, latest_email_id)
            if latest_email_id:
                user.latest_email_id = latest_email_id
                user.save(update_fields=['latest_email_id'])


def process_email(user, email, latest_email_id):
    from_email, subject, date, body, msg_id = email
    results = [analyze_email_content(body) for _ in range(3)]
    best_result = select_best_result(results)
    event_details = parse_best_result(best_result)
    obj, created = Email.objects.update_or_create(
        user=user,
        message_id=msg_id,
        defaults={'from_email': from_email, 'subject': subject, 'date': date, 'body': body,
                  'event_details': event_details}
    )
    return msg_id if not latest_email_id or msg_id > latest_email_id else latest_email_id


def parse_best_result(result):
    # 逻辑来格式化结果字符串
    return f"{result}"


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


def get_emails_from_db(user):
    emails = Email.objects.filter(user=user).order_by('-date')
    prepared_emails = []
    for email in emails:
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


def update_emails(user):
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
            event_details = parse_best_result(best_result)  # 假设这个方法定义了如何解析和格式化结果

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
        return True, get_emails_from_db(user)
    return False, []
