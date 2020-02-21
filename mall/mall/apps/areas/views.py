from django.shortcuts import render

# Create your views here.
from rest_framework import status, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin, ListCacheResponseMixin

from areas.models import Area
# from areas.serializers import UserAddressSerializer, AddressTitleSerializer


# class AreasView(GenericAPIView):
#     serializer_class = AreaSerializer
#     queryset = Area.objects.filter(parent=None)
#
#     def get(self, request):
#         ares = self.get_queryset()
#         s = self.get_serializer(ares, many=True)
#         return Response(s.data)
#
#
# class AreaView(GenericAPIView):
#     serializer_class = SubAreaSerializer
#     queryset = Area.objects.all()
#
#     def get(self, request, pk):
#         area = self.get_object()
#         s = self.get_serializer(area)
#         return Response(s.data)
#
#
# class AreaViewSet(GenericViewSet):
#
#     def get_queryset(self):
#         if self.action == 'get_areas':
#             return Area.objects.filter(parent=None)
#         else:
#             return Area.objects.all()
#
#     def get_serializer(self, *args, **kwargs):
#         if self.action == "get_areas":
#             return AreaSerializer
#         else:
#             return SubAreaSerializer
#     def list(self,request):
#         areas = self.get_queryset()
#         s = self.get_serializer(areas,many=True)
#         return Response(s.data)
#
#     def retrieve(self,request):
#         areas = self.get_object()
#         s = self.get_serializer(areas)
#         return Response(s.data)

# 因为使用了视图集没有视图函数，所以就有drf-extentions的拓展类可以用于list,retrieve方法
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreaViewSet(ReadOnlyModelViewSet):
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()
    def get_serializer_class(self):
        if self.action == "list":
            return AreaSerializer
        else:
            return SubAreaSerializer


# class AreaViewSet(ListCacheResponseMixin, ReadOnlyModelViewSet):
#     pagination_class = None  # 区划信息不分页
#
#     def get_queryset(self):
#         if self.action == "list":
#             return Area.objects.filter(parent=None)
#         else:
#             return Area.objects.all()
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return AreaSerializer
#         else:
#             return SubAreaSerializer
#
