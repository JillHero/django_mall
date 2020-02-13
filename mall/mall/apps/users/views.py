from django.shortcuts import render

# Create your views here.

#  usernames/(?P<username>\w{5,20})/count/
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from mall.apps.users import serializers
from users.models import User


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            "count": count
        }
        return Response(data, status=status.HTTP_200_OK)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data, status=status.HTTP_200_OK)


class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserDetailSerializer

    def get_object(self):
        user = self.request.user
        return user


class EmailView(UpdateAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self,*args,**kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self,request):
        token = request.query_params.get("token")
        if not token:
            return Response({"message":"缺少token"},status=status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({"message":"连接信息无效"},status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({"message":"ok"})