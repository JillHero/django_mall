from django.shortcuts import render

# Create your views here.
import pickle
import base64
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from carts.constants import CART_COOKIES_EXPIRES
from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSeriazlier
from goods.models import SKU


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

    def get(self, request):
        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            redis_cart_selected = redis_conn.smembers("selected_%s" % user.id)

            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }


        else:
            cookie_cart = request.COOKIES.get("cart")
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.decode()))
            else:
                cart_dict = {}

        sku_obj_list = SKU.objects.filter(id__in=cart_dict.keys())
        for sku in sku_obj_list:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        s = CartSKUSerializer(instance=sku_obj_list, many=True)
        return Response(s.data)

    def put(self, request):
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
            pl.hset("cart_%s" % user.id, sku_id, count)
            if selected:
                pl.sadd("selected_%s" % user.id, sku_id)
            else:
                pl.srem("selected_%s" % user.id, sku_id)
            pl.execute()
            return Response(s.data, status=status.HTTP_200_OK)
        else:
            cookies_cart = request.COOKIES.get("cart")
            if cookies_cart:
                cart_dict = pickle.loads(base64.b64decode(cookies_cart.encode()))
            else:
                cart_dict = {}

            response = Response(s.data)

            if sku_id in cart_dict:
                cart_dict[sku_id] = {
                    "count": count,
                    "selected": selected
                }
                cart_cookies = base64.b64encode(pickle.dumps(cart_dict)).decode()

                response.set_cookie("cart", cart_cookies, max_age=CART_COOKIES_EXPIRES)
            return response

    def delete(self, request):
        s = CartDeleteSeriazlier(data=request.data)
        s.is_valid(raise_exception=True)

        sku_id = s.validated_data['sku_id']
        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            pl.hdel("cart_%s" % user.id, sku_id)
            pl.srem("selected_%s" % user.ud, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            cookies_cart = request.COOKIES.get("cart")
            if cookies_cart:
                cart_dict = pickle.loads(base64.b64decode(cookies_cart.encode()))
            else:
                cart_dict = {}

            response = Response(status=status.HTTP_204_NO_CONTENT)
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie("cart",cart_cookie,max_age=CART_COOKIES_EXPIRES)
            return response
