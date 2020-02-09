from celery import Celery
import os

if not os.getenv("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = 'mall.settings.dev'
celery_app = Celery("mall")
celery_app.config_from_object("celery_tasks.config")


# 导入任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])