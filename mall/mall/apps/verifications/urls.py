from django.conf.urls import url

from mall.apps.verifications import views

urlpatterns = [
    url(r"image_codes/(?P<image_code_id>[\w-]+)/$", views.ImageCodeView.as_view())

]
