import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):

    # 获取cookie中的数据
    cookie_cart = request.COOKIES.get("cart")
    if not cookie_cart:
        return response

        # 解析数据
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
    # 获取redis数据
    redis_conn = get_redis_connection('cart')
    redis_cart = redis_conn.hgetall("cart_%s" % user.id)

    # 为了转换redis里字节类型
    cart = {}
    for sku_id, count in redis_cart.items():
        cart[int(sku_id)] = int(count)

    redis_cart_selected_add = []
    redis_cart_selected_remove = []

    """
    redis_cart = {
        '1':'20',
        '2':'2',
    }
    redis_cart_selected = set(1)

    cookie_cart = {
        1:
        {
        'count':10,
        'selected':True
        }
        2:{
        'count':20,
        'selected':False
        }
    }
    """

    for sku_id, count_selected_dict in cookie_cart_dict.items():
        # 处理商品的数量，维护在redis中数据数量的字典里
        cart[sku_id] = count_selected_dict['count']

        if count_selected_dict['selected']:
            redis_cart_selected_add.append(sku_id)
        else:
            redis_cart_selected_remove.append(sku_id)

    if cart:
        pl = redis_conn.pipeline()
        pl.hmset("cart_%s" % user.id, cart)
        if redis_cart_selected_remove:
            pl.srem("cart_selected_%s" % user.id, *redis_cart_selected_remove)
        if redis_cart_selected_add:
            pl.sadd("cart_selected_%s" % user.id, *redis_cart_selected_add)
        pl.execute()

    response.delete_cookie("cart")

    return response
