import json
import logging
from urllib.request import urlopen

import itsdangerous
from django.conf import settings
import urllib.parse

from itsdangerous import Serializer, BadData

from oauth import constants
from oauth.exception import OAuthAPIError

logger = logging.getLogger("django")


class OAuthQQ(object):
    def __init__(self, client_id=None, redirect_uri=None, state=None, client_secret=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI
        # self.state = state if state else settings.QQ_STATE
        self.state = state or settings.QQ_STATE  # 还可以使用or不是前面就是后面
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET

    def get_login_url(self):
        url = "https://graph.qq.com/oauth2.0/authorize?"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": self.client_id
        }

        url += urllib.parse.urlencode(params)
        return url

    def get_access_token(self, code):
        url = "https://graph.qq.com/oauth2.0/token?"
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        url += urllib.parse.urlencode(params)
        try:
            resp = urlopen(url)

            resp_data = resp.read()
            resp_data = resp_data.decode()
            resp_dict = urllib.parse.parse_qs(resp_data)
        except Exception as e:
            logger.error("获取access_token异常%s" % e)
            raise OAuthAPIError
        else:


            access_token = resp_dict.get("access_token")

            return access_token[0]

    def get_openid(self, access_token):
        url = "https://graph.qq.com/oauth2.0/me?access_token=" + access_token

        try:
            resp = urlopen(url)
            resp_data = resp.read()
            resp_data = resp_data.decode()
            resp_data = resp_data[10:-4]
            resp_dict = json.loads(resp_data)
        except Exception as e:
            logger.error("获取openid异常%s" % e)
            raise OAuthAPIError
        else:
            openid = resp_dict.get("openid")
            return openid

    def generate_bind_user_access_token(self, openid):
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                                  constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({"openid": openid})
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET_KEY,constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['openid']





# class OAuthQQ(object):
#     def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
#         self.client_id = client_id or settings.QQ_CLIENT_ID
#         self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
#         self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
#         self.state = state or settings.QQ_STATE
#
#     def get_qq_login_url(self):
#         params = {
#             "response_type": "code",
#             "client_id": self.client_id,
#             "redirect_uri": self.redirect_uri,
#             "state": self.state,
#             "scope": "get_user_info",
#
#         }
#         url = "https://graph.qq.com/oauth2.0/authorize?" + urllib.parse.urlencode(params)
#         return url
#
#     def get_access_token(self, code):
#         params = {
#             "grant_type": "authorization_code",
#             "client_id": self.client_id,
#             "code": code,
#             "client_secret": self.client_secret,
#             "redirect_uri": self.redirect_uri
#         }
#         url = "https://graph.qq.com/oauth2.0/token?" + urllib.parse.urlencode(params)
#         response = urlopen(url)
#         response_data = response.read().decode()
#         data = urllib.parse.parse_qs(response_data)
#         access_token = data.get("access_token", None)
#
#         if not access_token:
#             logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
#             raise OAuthAPIError()
#         return access_token[0]
#
#     def get_openid(self, access_token):
#         url = "https://graph.qq.com/oauth2.0/me?access_token=" + access_token
#         response = urlopen(url)
#         response_data = response.read().decode()
#         # callback({"client_id": "YOUR_APPID", "openid": "YOUR_OPENID"});
#         try:
#             data = json.loads(response_data[10:-4])
#         except Exception:
#             data = urllib.parse.parse_qs(response_data)
#             logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
#             raise OAuthAPIError()
#
#         openid = data.get("openid", None)
#         return openid
#
#     @staticmethod
#     def generate_save_user_token(openid):
#         serializer = Serializer(settings.SECRET_KEY,constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
#         data = {'openid': openid}
#         token = serializer.dumps(data)
#         return token.decode()