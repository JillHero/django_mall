from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

from rest_framework.response import Response

from goods.models import SKU
from orders.seriazliers import CartSKUSerializer, SaveOrderSerializer


class OrderSettlementView(GenericAPIView):
    serializer_class = CartSKUSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        redis_conn = get_redis_connection('cart')
        redis_cart_dict = redis_conn.hgetall("cart_%s" % user.id)
        redis_cart_selected = redis_conn.smembers("selected_%s" % user.id)
        cart = {}
        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(redis_cart_dict[sku_id])

        sku_id_list = cart.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)
        for sku in sku_obj_list:
            sku.count = cart[sku.id]
        freigth = Decimal('10.00')
        s = self.get_serializer(sku_obj_list, many=True)

        return Response({'freight': freigth,'skus': s.data})


class SaveOrderView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer
