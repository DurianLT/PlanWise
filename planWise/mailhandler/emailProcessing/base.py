from imapclient import IMAPClient
from email.header import decode_header
from email import message_from_bytes
import ssl


def loginTest(userName, password):
    HOST = 'outlook.office365.com'

    # 使用SSL连接
    context = ssl.create_default_context()

    try:
        with IMAPClient(HOST, ssl_context=context) as client:
            # 尝试登录
            client.login(userName, password)
            return True
    except Exception as e:
        return False


def getMailForID(userName, password, specific_msg_id):
    HOST = 'outlook.office365.com'
    # 使用SSL连接
    context = ssl.create_default_context()

    with IMAPClient(HOST, ssl_context=context) as client:
        # 登录
        client.login(userName, password)

        # 选择邮箱，使用readonly模式以防止意外地修改任何邮件
        client.select_folder('INBOX', readonly=True)

        results = []

        # 尝试获取指定邮件ID的邮件详细信息
        try:
            data = client.fetch([specific_msg_id], ['ENVELOPE', 'RFC822'])
            if specific_msg_id not in data:
                return "ID not found"

            data = data[specific_msg_id]
            envelope = data[b'ENVELOPE']
            email_message = message_from_bytes(data[b'RFC822'])  # 解析邮件字节

            # 解码发件人信息
            from_ = envelope.from_[0]
            from_decoded = "{}@{}".format(from_.mailbox.decode(), from_.host.decode())

            # 解码主题
            subject_encoded = envelope.subject
            if isinstance(subject_encoded, bytes):
                subject_encoded = subject_encoded.decode('utf-8', errors='replace')
            subject_decoded = decode_header(subject_encoded)
            subject = ''
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

                    # 跳过附件，只获取文本内容
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True).decode(part.get_content_charset(), 'replace')
                        break  # 可以根据需要调整逻辑，以获取 'text/html' 或其他格式的内容
            else:
                body = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), 'replace')

        except ValueError as e:
            print(e)
            'error'
        except Exception as e:
            print("An error occurred:", str(e))
            return 'error'

        results.append((from_decoded, subject, envelope.date, body, specific_msg_id))

        # 注销
        client.logout()

        return results


def getMailsForRange(userName, password, id_start, id_end):
    HOST = 'outlook.office365.com'
    context = ssl.create_default_context()

    with IMAPClient(HOST, ssl_context=context) as client:
        # 登录
        client.login(userName, password)

        # 选择邮箱，使用readonly模式以防止意外地修改任何邮件
        client.select_folder('INBOX', readonly=True)

        # 存储结果的列表
        results = []

        # 遍历指定的ID范围
        for msg_id in range(id_start, id_end + 1):
            try:
                data = client.fetch([msg_id], ['ENVELOPE', 'RFC822'])
                if msg_id not in data:
                    continue  # 如果邮件ID不存在，则跳过

                data = data[msg_id]
                envelope = data[b'ENVELOPE']
                email_message = message_from_bytes(data[b'RFC822'])

                # 解码发件人信息
                from_ = envelope.from_[0]
                from_decoded = "{}@{}".format(from_.mailbox.decode(), from_.host.decode())

                # 解码主题
                subject_encoded = envelope.subject
                if isinstance(subject_encoded, bytes):
                    subject_encoded = subject_encoded.decode('utf-8', errors='replace')
                subject_decoded = decode_header(subject_encoded)
                subject = ''
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
                    body = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), 'replace')

                # 添加到结果列表
                results.append((from_decoded, subject, envelope.date, body, msg_id))

            except Exception as e:
                print(f"Error fetching mail ID {msg_id}: {str(e)}")

        # 注销
        client.logout()

        return results


def getMailsForIDs(userName, password, ids):
    HOST = 'outlook.office365.com'
    context = ssl.create_default_context()

    with IMAPClient(HOST, ssl_context=context) as client:
        # 登录
        client.login(userName, password)

        # 选择邮箱，使用readonly模式以防止意外地修改任何邮件
        client.select_folder('INBOX', readonly=True)

        # 存储结果的列表
        results = []

        # 遍历ID列表
        for msg_id in ids:
            try:
                data = client.fetch([msg_id], ['ENVELOPE', 'RFC822'])
                if msg_id not in data:
                    continue  # 如果邮件ID不存在，则跳过

                data = data[msg_id]
                envelope = data[b'ENVELOPE']
                email_message = message_from_bytes(data[b'RFC822'])

                # 解码发件人信息
                from_ = envelope.from_[0]
                from_decoded = "{}@{}".format(from_.mailbox.decode(), from_.host.decode())

                # 解码主题
                subject_encoded = envelope.subject
                if isinstance(subject_encoded, bytes):
                    subject_encoded = subject_encoded.decode('utf-8', errors='replace')
                subject_decoded = decode_header(subject_encoded)
                subject = ''
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
                    body = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), 'replace')

                # 添加到结果列表
                results.append((from_decoded, subject, envelope.date, body, msg_id))

            except Exception as e:
                print(f"Error fetching mail ID {msg_id}: {str(e)}")

        # 注销
        client.logout()

        return results


def getNewID(userName, password):
    HOST = 'outlook.office365.com'

    # 使用SSL连接
    context = ssl.create_default_context()

    with IMAPClient(HOST, ssl_context=context) as client:
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
    HOST = 'outlook.office365.com'

    # 使用SSL连接
    context = ssl.create_default_context()

    with IMAPClient(HOST, ssl_context=context) as client:
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
