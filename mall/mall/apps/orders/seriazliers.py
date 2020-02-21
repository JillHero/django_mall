from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
import logging

logger = logging.getLogger('django')


class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class SaveOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('address', 'pay_method', 'order_id')
        extra_kwargs = {
            'order_id': {
                'read_only': True
            },
            'address': {
                "write_only": True
            },
            'pay_method': {
                'required': True
            }
        }

    def create(self, validated_data):
        address = validated_data['address']
        pay_method = validated_data['pay_method']
        # 获取用户对象
        user = self.context['request'].user

        # 查询购物车redis sku_id count selected
        redis_conn = get_redis_connection('cart')
        redis_cart_dict = redis_conn.hgetall("cart_%s" % user.id)
        redis_cart_selected = redis_conn.smembers("selected_%s" % user.id)
        cart = {}

        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(redis_cart_dict[sku_id])
        if not cart:
            raise serializers.ValidationError("没有需要结算的商品")
        # 查询商品数据库,获取商品数据
        sku_id_list = cart.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)
        # 创建事务
        with transaction.atomic():
            try:
                # 创建保存点
                save_id = transaction.savepoint()
                # 保存订单
                # 生成订单编号order_id
                # 20200221151010 用户id
                order_id = timezone.now().strftime('%Y%m%d%H%M%S') + str(user.id)
                # 创建订单基本信息表记录 Orderinfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal("0"),
                    freight=Decimal("10"),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM[
                        'UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM[
                        'UNPAID']
                )

                # 遍历需要结算的商品数据
                for sku in sku_obj_list:
                    sku_count = cart[sku.id]
                    # 判断库存

                    if sku.stock < sku_count:
                        # 回滚到保存点
                        transaction.savepoint_rollback(save_id)
                        raise serializers.ValidationError("库存不足")
                    # 库存减少 销量增加
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()
                    order.total_count += sku_count
                    order.total_amount += (sku.price * sku_count)
                    # 创建订单商品信息表记录 OrderGoods
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )
                order.save()
            except serializers.ValidationError:
                raise
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise
            else:
                transaction.savepoint_commit(save_id)
            # 删除购物车中的以结算商品

        pl = redis_conn.pipeline()
        pl.hdel("cart_%s" % user.id, *redis_cart_selected)
        pl.srem("selected_%s" % user.id, *redis_cart_selected)
        pl.execute()
        # 返回OrderInfo对象
        return OrderInfo
