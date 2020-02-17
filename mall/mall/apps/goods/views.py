from django.shortcuts import render

# Create your views here.
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', "price", "sales")


    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]
    serializer_class = SKUIndexSerializer