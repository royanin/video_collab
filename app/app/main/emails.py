from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import boto3

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


def send_mail_by_aws(from_email, to_emails, email_subject, body):
    ses = boto3.client('ses',region_name=current_app.config['AWS_REGION'],
                        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
                        aws_secret_access_key=current_app.config['AWS_ACCESS_KEY_SECRET'])

    try:
        ses.send_email(
        Source=from_email,
        Destination={'ToAddresses': [to_emails]},
        Message={
            'Subject': {'Data': email_subject},
            'Body': {
                'Text': {'Data': body},
                'Html':{'Data': body}
            }
        }
        )
        return "success"
    except Exception as e:
        print(e.message)
        return "failed"


def send_email(from_email, to_emails, email_subject, body):
    mail_handler=current_app.config['MAIL_HANDLER']
    if mail_handler=='sg':
        msg = send_mail_by_sg(from_email, to_emails, email_subject, body)
        return msg
    elif mail_handler=='aws':
        msg = send_mail_by_aws(from_email, to_emails, email_subject, body)
        return msg
