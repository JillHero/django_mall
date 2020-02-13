import itsdangerous
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from itsdangerous import BadData

from users import constants


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")

    class Meta:
        db_table = "tb_users"  # 数据库表名
        verbose_name = "用户"  # admin站点中的名称
        verbose_name_plural = verbose_name  # 显示复数的名称

    def generate_verify_email_url(self):
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                                  expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {"user_id": self.id, "email": self.email}
        token = serializer.dumps(data).decode()
        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=" + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                                  expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None

        else:
            user_id = data['user_id']
            email = data['email']
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None

            else:

                return user
