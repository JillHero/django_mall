from django.shortcuts import render

# Create your views here.
import pickle
import base64
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from carts.constants import CART_COOKIES_EXPIRES
from carts.serializers import CartSerializer


class CartView(GenericAPIView):
    serializer_class = CartSerializer

    def perform_authentication(self, request):
        pass

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        sku_id = s.validated_data['sku_id']
        count = s.validated_data['count']
        selected = s.validated_data['selected']

        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            pl.hincrby("cart_%s" % user.id, sku_id, count)
            if selected:
                pl.sadd("selected_%s" % user.id, sku_id)
            pl.execute()
            return Response(data=s.data, status=status.HTTP_200_OK)
        else:
            cart_str = request.COOKIES.get("cart")
            if cart_str:
                cart_byte = cart_str.decode()
                b_byte = base64.b64decode(cart_byte)
                cart_dict = pickle.loads(b_byte)

            else:
                cart_dict = {}

            if sku_id in cart_dict:
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected

            else:
                cart_dict[sku_id] = {
                    'count': count,
                    "selected": selected
                }

            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = Response(s.data)
            response.set_cookie('cart', cart_cookie, max_age=CART_COOKIES_EXPIRES)
            return response
