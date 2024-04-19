import html
import re
from imapclient import IMAPClient
from email.header import decode_header
from email import message_from_bytes
import ssl


def clean_text(text):
    """清理邮件正文中的多余空格并保留换行"""
    # 只移除行内的多余空格，不影响换行符
    lines = text.splitlines()
    cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in lines]
    # 使用html.unescape处理HTML实体
    cleaned_text = html.unescape('\n'.join(cleaned_lines))
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
                body = part.get_payload(decode=True).decode(part.get_content_charset(), 'replace')
                break
    else:
        text = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), 'replace')
        body = clean_text(text)

    return from_decoded, subject, envelope.date, body


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
