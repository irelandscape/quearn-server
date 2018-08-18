from django.conf.urls import url
from steem import views

urlpatterns = [
  url(r'^steemuser/$', views.steemuser),
  url(r'^favourite_topic/$', views.favourite_topic),
  url(r'^topic/$', views.topic),
]
