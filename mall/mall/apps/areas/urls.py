from django.conf.urls import url

from areas import views

urlpatterns = [
    # url(r"^areas/$",views.AreasView.as_view()),
    # url(r"^areas/(?P<pk>\d+)/$",views.AreaView.as_view())
    url(r"^areas/(?P<pk>\d+)/$", views.AreaViewSet.as_view({"get": "retrieve"})),
    url(r"^areas/", views.AreaViewSet.as_view({"get": "list"}))
]
