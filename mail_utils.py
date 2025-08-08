import datetime
import json
import queue
import smtplib, ssl
import threading
import traceback

from config import logger, smtp_server, smtp_port, sender_mail, sender_password, sender_username, page_url, admin_url

context = ssl.create_default_context()
server = None
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def connect_email():
    try:
        logger.info(f"connecting mail server..")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_username, sender_password)
        return server
    except Exception as e:
        logger.error(f"error in connecting mail {e}")
        return None


def send_email(receiver, subject="", username="", msg_data="", mail_type="", user_data_dict={}):
    logger.info(msg_data)
    threading.Thread(target=sending_email,
                     args=(receiver, subject, username, msg_data, mail_type, user_data_dict,)).start()


def sending_email(receiver='', subject="", username="", msg_data="", mail_type="", user_data_dict={}):
    try:
        logger.info(f"sending mail {receiver}    {msg_data}     mail_type {mail_type}")
        # receiver = 'ermohitgupta.16@gmail.com'
        msg_data = receiver
        if isinstance( receiver, list):
            msg_data = ', '.join(receiver)
        mail_server_object = connect_email()
        if mail_server_object == None:
            logger.error(f"error in mail connection ")
        else:
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_mail
            msg['To'] = 'ermohitgupta.16@gmail.com'
            msg['UserName'] = sender_username
            # Create the body of the message (a plain-text and an HTML version).
            # text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
            html = None
            if mail_type == "disconnect":
                receiver = admin_url
                msg['Subject'] = subject
                html = disconnect(msg_data)
            elif mail_type == "connected":
                receiver = admin_url
                msg['Subject'] = subject
                html = connected(msg_data)
            else:
                return

            part1 = MIMEText(html, 'html')
            msg.attach(part1)
            logger.info(f"sending mail")
            mail_server_object.sendmail(sender_mail, receiver, msg.as_string())
    except Exception as e:
        logger.error(f"error in sending  mail error msg [ {e} ] {subject} to {receiver}     {traceback.format_exc()}")


def connected(msg_data):
    # <li>A short tutorial video is available to guide you through this process.</li>
    # if msg_data != "":
    #     msg_data = "<b>ProjectX Response: </b>" + msg_data + "<br><br>"
    return """
     <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title></title>
</head>
<body>

<b>Dear </b>""" + msg_data + """<br><br>
I hope this message finds you well.
 <br><br>
We are pleased to inform you that your ProjectX account has been <b>successfully connected</b>.
 <br><br>

If you need any assistance, please don't hesitate to contact our support team at [<a href="support@pickmytrade.com">support@pickmytrade.com</a> / <a href="https://discord.gg/M5CJsVZt2P">Discord Server</a>].
  <br><br>

Best regards,<br>
Support Team 
</body>
</html>
"""


def disconnect(msg_data):
    # <li>A short tutorial video is available to guide you through this process.</li>
    # if msg_data != "":
    #     msg_data = "<b>ProjectX Response: </b>" + msg_data + "<br><br>"
    return """
     <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title></title>
</head>
<body>

<b>Dear </b> """ + msg_data + """<br><br>
I hope this message finds you well.
 <br><br>
We have been experiencing ongoing issues with the projectx connection and have tried multiple times to establish a stable connection.
 Unfortunately, all attempts so far have been unsuccessful.<br> Try to re-connect by <b> """ + page_url + """ </b> .
 <br><br>
If you need any assistance, please don't hesitate to contact our support team at [<a href="support@pickmytrade.com">support@pickmytrade.com</a> / <a href="https://discord.gg/M5CJsVZt2P">Discord Server</a>].
  <br><br>

Best regards,<br>
Support Team 
</body>
</html>
"""

