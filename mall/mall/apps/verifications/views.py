import random

from django.http import HttpResponse
import logging
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from mall.apps.verifications import constants
from mall.apps.verifications.serializers import ImageCodeCheckSerializer
from mall.libs.captcha.captcha import captcha
from mall.utils.yuntongxun import sms
from celery_tasks.sms.tasks import send_sms_code

logger = logging.getLogger("django")


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type="image/jpg")


class SMSCodeView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        s = self.get_serializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        sms_code = '%06d' % random.randint(0, 999999)
        redis_conn = get_redis_connection("verify_codes")
        # redis 管道
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        # try:
        #     ccp = sms.CCP()
        #     expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        #     result = ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error("发送短信验证码异常[mobile:%s,message:%s]" % (mobile, e))
        #     return Response({"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     if result == 0:
        #         logger.info("发送短信验证码正常[mobile:%s]" % mobile)
        #         return Response({"message": "OK"}, status=status.HTTP_200_OK)
        #     else:
        #         logger.error("发送短信验证码失败[mobile:%s]" % mobile)
        #         return Response({"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 使用celery发送短信验证码

        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)
        return Response({"message": "OK"}, status=status.HTTP_200_OK)
