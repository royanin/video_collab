from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_mail_by_sg(from_email, to_emails, email_subject, body):
    message = Mail(
    from_email=from_email,
    to_emails=to_emails,
    subject=email_subject,
    html_content=body)

    try:
        sg = SendGridAPIClient(current_app.config['SG_MAIL_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return "success"
    except Exception as e:
        print(e.message)
        return "failed"


def send_email(from_email, to_emails, email_subject, body, mail_handler='sg'):
    if mail_handler=='sg':
        msg = send_mail_by_sg(from_email, to_emails, email_subject, body)
        return msg
