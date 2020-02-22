import os

from alipay import AliPay
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from orders.models import OrderInfo


class PaymentView(APIView):
    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                                          paymethod=OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
        except OrderInfo.DoesNotExist:
            return Response({"message": "订单信息有误"}, status=status.HTTP_400_BAD_REQUEST)
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            alipay_public_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "keys/app_public_key.pem"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_ment),
            subject='我和可爱，请亏我全%s' % order_id,
            return_url=settings.RETURN_URL,
            notify_url=None
        )
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return Response({"aplipay_url": alipay_url})
