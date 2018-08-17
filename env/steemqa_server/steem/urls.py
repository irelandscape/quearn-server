from django.conf.urls import url
from steem import views

urlpatterns = [
  url(r'^steemuser/$', views.api_steemusers),
  url(r'^steemuser/(?P<pk>[0-9]+)/$', views.api_steemuser_details),
]
