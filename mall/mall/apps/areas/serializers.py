import re

from rest_framework import serializers

from users.models import Address


from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name")


class SubAreaSerializer(serializers.ModelSerializer):
    subs = AreaSerializer(many=True,read_only=True)
    class Meta:
        model = Area
        fields = ("id", "name", "subs")        # depth = 1 只会展示上一级 一的一方的具体信息