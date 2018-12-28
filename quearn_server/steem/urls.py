from django.conf.urls import url
from steem import views

urlpatterns = [
  url(r'^api/steemusers/$', views.SteemUserView.as_view()),
  url(r'^api/favourite_topics/$', views.FavouriteTopicList.as_view()),
  url(r'^api/favourite_topics/(?P<pk>[0-9]+)/$', views.FavouriteTopicItem.as_view()),
  url(r'^api/topics/$', views.topic),
  url(r'^api/configs/$', views.ConfigList.as_view()),
  url(r'^api/help/$', views.HelpView.as_view()),
  url(r'^api/scrapers/$', views.ScraperList.as_view()),
  url(r'^api/scrapers/(?P<pk>[0-9]+)/$', views.ScraperItem.as_view()),
  url(r'^api/questions/$', views.QuestionView.as_view()),
  url(r'^api/questions/(?P<pk>[0-9]+)/$', views.QuestionItem.as_view()),
  url(r'^api/questions/count$', views.question_count),
  url(r'^api/newquestion$', views.NewQuestion.as_view()),
  url(r'^api/answers/$', views.AnswerView.as_view()),
  url(r'^api/answers/count$', views.answer_count),
  url(r'^api/newanswer$', views.NewAnswer.as_view()),
  url(r'^api/bookmarks/$', views.BookmarkList.as_view()),
  url(r'^api/bookmarks/(?P<pk>[0-9]+)/$', views.BookmarkItem.as_view()),
]
