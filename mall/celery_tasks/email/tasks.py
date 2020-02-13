from django.core.mail import send_mail
from django.conf import settings

from celery_tasks.main import celery_app


@celery_app.task(name="send_active_email")
def send_active_email(to_email, verify_url):
    subject = "邮箱验证"
    html_message = '<p>邮箱为%s</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
