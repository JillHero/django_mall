from django.shortcuts import render

# Create your views here.
from rest_framework import request, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.exception import OAuthAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import QAuthQQUserSerizlizer
from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    def get(self, request):
        next = request.query_params.get("next")

        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_login_url()
        return Response({"login_url": login_url})


class QQAuthUserView(CreateAPIView):
    serializer_class = QAuthQQUserSerizlizer

    def get(self, request):
        code = request.query_params.get("code")
        print(code)
        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)

        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            print(access_token)
            openid = oauth_qq.get_openid(access_token)
            print(openid)
        except OAuthAPIError:
            return Response({"message": "访问QQ接口异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({"access_token": access_token})
        else:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            response = Response({
                "username": user.username,
                "user_id": user.id,
                "token": token
            })
            response = merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self, request, *args, **kwargs):
        response = super(QQAuthUserView, self).post(request, *args, **kwargs)
        user = self.user
        response = merge_cart_cookie_to_redis(request, user, response)
        return response
