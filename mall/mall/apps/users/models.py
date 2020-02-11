from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False,verbose_name="邮箱验证状态")


    class Meta:
        db_table = "tb_users"  # 数据库表名
        verbose_name = "用户"  # admin站点中的名称
        verbose_name_plural = verbose_name  # 显示复数的名称
