from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from mall.apps.users import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r"^usernames/(?P<username>\w{5,20})/count/$", views.UsernameCountView.as_view()),
    url(r"^mobiles/(?P<mobile>1[3-9]\d{9})/count/$", views.MobileCountView.as_view()),
    url(r"^authorizations/$", obtain_jwt_token),  # 使用jwt的登陆视图
    url(r"^user/$", views.UserDetailView.as_view()),
    url(r"^emails/$", views.EmailView.as_view()),
    url(r"^emails/verification/$", views.VerifyEmailView.as_view())
]
