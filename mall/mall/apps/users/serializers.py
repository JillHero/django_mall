import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from celery_tasks.email.tasks import send_active_email
from goods.models import SKU
from users.constants import USER_HISTORY_LIMIT
from users.models import User, Address


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.CharField(label="同意协议", write_only=True)
    token = serializers.CharField(label="JWT token", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "password2", "sms_code", "mobile", "allow", "token")
        extra_kwargs = {
            "username": {
                "min_length": 5,
                "max_length": 20,
                "error_messages": {
                    "min_length": "仅允许5-20个字符的用户名",
                    "max_length": "仅允许5-20个字符的用户名",
                },
            },
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 20,
                "error_messages": {
                    "min_length": "仅允许8-20个字符的用户名",
                    "max_length": "仅允许8-20个字符的用户名"
                },
            }

        }

    def validate_mobile(self, value):
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("手机号格式错误")
        return value

    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError("请同意用户协议")

    def validate(self, attrs):
        if not attrs.get("password") == attrs.get("password2"):
            raise serializers.ValidationError("两次密码输入不一致")

        redis_conn = get_redis_connection("verify_codes")
        mobile = attrs.get("mobile")
        real_sms_code = redis_conn.get("sms_%s" % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError("无效的短信验证码")
        if attrs.get("sms_code") != real_sms_code.decode():
            raise serializers.ValidationError("短信验证码错误")
        return attrs

    def create(self, validated_data):
        del validated_data["sms_code"]
        del validated_data["password2"]
        del validated_data["allow"]
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "mobile", "email", "email_active")


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")

    def update(self, instance, validated_data):
        email = validated_data["email"]
        instance.email = email
        instance.save()
        url = instance.generate_verify_email_url()

        send_active_email.delay(email, url)
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label="省ID", required=True)
    city_id = serializers.IntegerField(label="市ID", required=True)
    district_id = serializers.IntegerField(label="区ID", required=True)

    class Meta:
        model = Address
        exclude = ("user", "is_deleted", "create_time", "update_time")

    def validate_mobile(self, value):
        if not re.match(r"1[3-9]\d{9}", value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("title",)


class AddUserBrowsingHistortSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("该商品不存在")
        return value

    def create(self, validated_data):
        sku_id = validated_data["sku_id"]
        user = self.context['request'].user
        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()
        redis_key = "history_%s" % user.id

        pl.lrem(redis_key, 0, sku_id)
        pl.lpush(redis_key, sku_id)
        pl.ltrim(redis_key, 0, USER_HISTORY_LIMIT - 1)
        pl.execute()
        return validated_data


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ("id", "name", "price", "default_image_url", "comments")
