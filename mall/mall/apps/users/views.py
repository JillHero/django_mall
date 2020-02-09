from django.shortcuts import render

# Create your views here.

#  usernames/(?P<username>\w{5,20})/count/
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mall.apps.users.models import User


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
