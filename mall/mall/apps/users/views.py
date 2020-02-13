from django.shortcuts import render

# Create your views here.

#  usernames/(?P<username>\w{5,20})/count/
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from mall.apps.users import serializers
from users import constants
from users.models import User
from users.serializers import AddressTitleSerializer, UserAddressSerializer


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

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"message": "缺少token"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({"message": "连接信息无效"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({"message": "ok"})


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({"message": "保存地址数据已满"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def list(self, request):
        queryset = self.get_queryset()
        s = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response(
            {
                "user_id": user.id,
                "default_address_id": user.default_address_id,
                "limit": constants.USER_ADDRESS_COUNTS_LIMIT,
                "addresses": s.data
            }
        )

    def destory(self, request, pk):
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        address = self.get_object()
        s = AddressTitleSerializer(address, data=request.data)
        s.is_valid()
        s.save()
        return Response(s.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({"message": "ok"}, status=status.HTTP_200_OK)
