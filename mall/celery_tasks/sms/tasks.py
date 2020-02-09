from celery_tasks.main import celery_app
from celery_tasks.sms.utils.yuntongxun import sms
import logging

logger = logging.getLogger("django")


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expires, temp_id):
    try:
        ccp = sms.CCP()
        result = ccp.send_template_sms(mobile, [sms_code, expires], temp_id)
    except Exception as e:
        logger.error("发送短信验证码异常[mobile:%s,message:%s]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送短信验证码正常[mobile:%s]" % mobile)
        else:
            logger.error("发送短信验证码失败[mobile:%s]" % mobile)
