import os

from alipay import AliPay
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from orders.models import OrderInfo
from payment.models import Payment


class PaymentView(APIView):
    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                                          pay_method=OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
        except OrderInfo.DoesNotExist:
            return Response({"message": "订单信息有误"}, status=status.HTTP_400_BAD_REQUEST)

        # 构造支付宝支付链接地址

        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string="""-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAt1WAmhHmKnxNSc1JqllAJKozRHeYcX9gTXZqrmsE38p1uMwD
W1IEdgw0oxhhNPkNuff/17rCHX3qXA7tscJpHin/TCvEoubYW7GkpN1CMaA/hcG2
fqgEg3KflV3py7ldIf719FYc3/yufkrXkF+FGPrL6TLo03+kiC3cwdUR5Fmy1JzQ
p3s7FxNFr9GF4g/F1RfupP5O86ivUmcaxgiwfs2I5dKrakcEi30HMTQLdTd6xfIb
VNKh/OV1RnFc4X8LDl45BDasTcKoVwsaoXkWUoy3EdcE6DRE1OMBtj4Ax1z/K2pk
24f/d28JldZOqut5SYmWmvSJtB92Vu+xkxb5cQIDAQABAoIBAFakNc6aPug9Lll+
hx3WaBXryabFzml1BRIWsHwVX4xTpibbY4q4zBrt0cJyNx5NxUrqBSLyw+IkK6mt
9G9ZrUvwFRLubFOAPSe4YFL5rdq+HMcdsR1SUi+87+YrJ957j6QNVjdOqv6/78cH
n7A/NCuF+vAOezHY1Oz2n6mLBJWhcPq9nR4mSD29CvMQ0p7pNyx8UOmG5nQGHKYN
EAG7S5iI18Ok6jIIpUTwjxrk051dK2kZeW4cpbOxSz681Ysecp5WsrlBLifdVcm3
HUDliGcUJ+64D7Kxbrdfh0AJI3No2hpGnz8sTlbmMjsbaX38CqdRVXKG5A8NBcts
uANAukECgYEA6/HUljzYS1PaWlr19s/UKTniobGwwZ1X+9RwzVZ4NNm/3BUZudnD
XwQONiIL00u+o6bCS3vT57f1PXlLlw6pJjsIIW2Tt42oJr4KhW93Cetr0bTkGIGK
sAcMJf2r+nGyYKI2P9NEa+N3jR5qLw7vS3S9DvFZJviMepMFrCoERzUCgYEAxurc
ZbJi4B/Aqqk768eUdyp4eKSuybetswcfai0/XuHRZnz4cNRNGZBgqmoDK0hg7hTM
RiW3DOv5+uaSWK+XZF9o3NZhkGXyhT4KehWVqPrg5VbdlBG/4vTNDNraRQyH009w
LEIPbM19izOQt+HEO46snmCaX1glvT26L1VcpM0CgYEA0CP328k1Lc59M3RGw0I3
8V5lNSshuMtrEHcqQ5piVI07GZVrqm4WUb2sI8kJEY8iUBAOGrTUDPhVWbOlIU8H
nPg6hfK6exR2ICdJ9MiOBKwv40Fmbs/oXrz41JLhof+m0mSG4usm0t5JWq5YEcdl
BfWnyoTSlvRwSLlmKaivOXkCgYAwnVvKGwPhRMFgtEWpxTg6u41/5re1Iwf3tiju
WSqgtM3pn2dUo/5H3ipR2+D0ZhcSeNDH4BXRuaZ5tHpV5Gw6orrNJjPoB5JzEAud
dMMD7nSieE1lD8V24V9v4djwgTR853BB0M9WRw6Ew9B9sFa2O5NijbeMz81BZ+Gm
CdW/jQKBgG+gxnmrWW7NPLyLTwVb935sKz9VtQ9vd9P0mu87NfwhPi4NxvvUKRIo
GDJby0QuzRyNO1j69Tmk+NrGyTGj6UyIyvVsUtS6OcSL3ptPaX7wY8hNxqyOc3/L
I6K2iKi2ch+9YnRNz5JYcarg6xTNr74mXs+vYKOvhPTux4h5C2Gw
-----END RSA PRIVATE KEY-----
""",
            alipay_public_key_string="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvrKwH2u3tQeXy6KC1GvqQ3+2WKwKZ6cCeDFEZvQAugRKT5elH4C2iiArhGY3/nqQyrbVtyQsmkJ7J+OGMQ8ARnHnucE3c2QACwMRfa4gPZjYznGe+89d2tuiWRD8YtMoPoM9qKzRE7AyAqNbkj9tnYwN9E06uUtx0w8DxBL/8yysm6KNSr7ZdUyHT+wYjGLJQaz2V3pg3YWo6VuvOu8CFf0lZ+kV5yki6Ra6zkqZBq0A7mtsISpoefiE47HYWQWi+PKixycHdWSvhlg7ye5iudriHAvbP4tMMuEoNrwqhFzwt8jj7Okr1A8Mn+PKS46mR0hfHCCU3XcO1byEFECs9wIDAQAB
-----END PUBLIC KEY-----
            """,
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='我和可爱，请亏我全%s' % order_id,
            return_url=settings.RETURN_URL,
            notify_url=None
        )
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return Response({"alipay_url": alipay_url})


class PaymentStatusView(APIView):
    def put(self,request):
        alipay_req_data = request.query_params
        if not alipay_req_data:
            return Response({"message":"缺少参数"},status=status.HTTP_400_BAD_REQUEST)
        alipay_req_dict = alipay_req_data.dict()
        sign = alipay_req_dict.pop("sign")
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string="""-----BEGIN RSA PRIVATE KEY-----
        MIIEowIBAAKCAQEAt1WAmhHmKnxNSc1JqllAJKozRHeYcX9gTXZqrmsE38p1uMwD
        W1IEdgw0oxhhNPkNuff/17rCHX3qXA7tscJpHin/TCvEoubYW7GkpN1CMaA/hcG2
        fqgEg3KflV3py7ldIf719FYc3/yufkrXkF+FGPrL6TLo03+kiC3cwdUR5Fmy1JzQ
        p3s7FxNFr9GF4g/F1RfupP5O86ivUmcaxgiwfs2I5dKrakcEi30HMTQLdTd6xfIb
        VNKh/OV1RnFc4X8LDl45BDasTcKoVwsaoXkWUoy3EdcE6DRE1OMBtj4Ax1z/K2pk
        24f/d28JldZOqut5SYmWmvSJtB92Vu+xkxb5cQIDAQABAoIBAFakNc6aPug9Lll+
        hx3WaBXryabFzml1BRIWsHwVX4xTpibbY4q4zBrt0cJyNx5NxUrqBSLyw+IkK6mt
        9G9ZrUvwFRLubFOAPSe4YFL5rdq+HMcdsR1SUi+87+YrJ957j6QNVjdOqv6/78cH
        n7A/NCuF+vAOezHY1Oz2n6mLBJWhcPq9nR4mSD29CvMQ0p7pNyx8UOmG5nQGHKYN
        EAG7S5iI18Ok6jIIpUTwjxrk051dK2kZeW4cpbOxSz681Ysecp5WsrlBLifdVcm3
        HUDliGcUJ+64D7Kxbrdfh0AJI3No2hpGnz8sTlbmMjsbaX38CqdRVXKG5A8NBcts
        uANAukECgYEA6/HUljzYS1PaWlr19s/UKTniobGwwZ1X+9RwzVZ4NNm/3BUZudnD
        XwQONiIL00u+o6bCS3vT57f1PXlLlw6pJjsIIW2Tt42oJr4KhW93Cetr0bTkGIGK
        sAcMJf2r+nGyYKI2P9NEa+N3jR5qLw7vS3S9DvFZJviMepMFrCoERzUCgYEAxurc
        ZbJi4B/Aqqk768eUdyp4eKSuybetswcfai0/XuHRZnz4cNRNGZBgqmoDK0hg7hTM
        RiW3DOv5+uaSWK+XZF9o3NZhkGXyhT4KehWVqPrg5VbdlBG/4vTNDNraRQyH009w
        LEIPbM19izOQt+HEO46snmCaX1glvT26L1VcpM0CgYEA0CP328k1Lc59M3RGw0I3
        8V5lNSshuMtrEHcqQ5piVI07GZVrqm4WUb2sI8kJEY8iUBAOGrTUDPhVWbOlIU8H
        nPg6hfK6exR2ICdJ9MiOBKwv40Fmbs/oXrz41JLhof+m0mSG4usm0t5JWq5YEcdl
        BfWnyoTSlvRwSLlmKaivOXkCgYAwnVvKGwPhRMFgtEWpxTg6u41/5re1Iwf3tiju
        WSqgtM3pn2dUo/5H3ipR2+D0ZhcSeNDH4BXRuaZ5tHpV5Gw6orrNJjPoB5JzEAud
        dMMD7nSieE1lD8V24V9v4djwgTR853BB0M9WRw6Ew9B9sFa2O5NijbeMz81BZ+Gm
        CdW/jQKBgG+gxnmrWW7NPLyLTwVb935sKz9VtQ9vd9P0mu87NfwhPi4NxvvUKRIo
        GDJby0QuzRyNO1j69Tmk+NrGyTGj6UyIyvVsUtS6OcSL3ptPaX7wY8hNxqyOc3/L
        I6K2iKi2ch+9YnRNz5JYcarg6xTNr74mXs+vYKOvhPTux4h5C2Gw
        -----END RSA PRIVATE KEY-----
        """,
            alipay_public_key_string="""-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvrKwH2u3tQeXy6KC1GvqQ3+2WKwKZ6cCeDFEZvQAugRKT5elH4C2iiArhGY3/nqQyrbVtyQsmkJ7J+OGMQ8ARnHnucE3c2QACwMRfa4gPZjYznGe+89d2tuiWRD8YtMoPoM9qKzRE7AyAqNbkj9tnYwN9E06uUtx0w8DxBL/8yysm6KNSr7ZdUyHT+wYjGLJQaz2V3pg3YWo6VuvOu8CFf0lZ+kV5yki6Ra6zkqZBq0A7mtsISpoefiE47HYWQWi+PKixycHdWSvhlg7ye5iudriHAvbP4tMMuEoNrwqhFzwt8jj7Okr1A8Mn+PKS46mR0hfHCCU3XcO1byEFECs9wIDAQAB
        -----END PUBLIC KEY-----
                    """,
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        result = alipay_client.verify(alipay_req_dict,sign)
        if result:
            order_id = alipay_req_dict.get("out_trade_on")
            trade_id = alipay_req_dict.get("trade_no")
            Payment.objects.create(
                order_id = order_id,
                trade_id = trade_id
            )
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            return Response({"trade_id":trade_id})
        else:
            return Response({"message":"参数有误"},status=status.HTTP_400_BAD_REQUEST)
