from django.conf.urls import url
from steem import views

urlpatterns = [
  url(r'^steemusers/$', views.SteemUserView.as_view()),
  url(r'^favourite_topics/$', views.FavouriteTopicList.as_view()),
  url(r'^favourite_topics/(?P<pk>[0-9]+)/$', views.FavouriteTopicItem.as_view()),
  url(r'^topics/$', views.topic),
  url(r'^configs/$', views.ConfigList.as_view()),
  url(r'^scrapers/$', views.ScraperList.as_view()),
  url(r'^scrapers/(?P<pk>[0-9]+)/$', views.ScraperItem.as_view()),
  url(r'^questions/$', views.QuestionView.as_view()),
  url(r'^questions/count$', views.question_count),
  url(r'^newquestion$', views.NewQuestion.as_view()),
  url(r'^answers/$', views.AnswerView.as_view()),
  url(r'^answers/count$', views.answer_count),
]
