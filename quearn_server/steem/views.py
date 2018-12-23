import hashlib
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from steem.models import *
from steem.serializers import *
from steemconnect.client import Client
from quearn_server.settings import STEEMCONNECT_CLIENT_ID
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.filters import OrderingFilter
import json
import urllib
import dateparser
from datetime import datetime
import django_filters
from django_filters import rest_framework

def sha512 (token) :
  hash = hashlib.sha512(token.encode('utf-8'))
  return hash.hexdigest()

def check_user (func) :
  def wrapper (self, *args, **kwargs) :
    username = ''
    access_token = ''
    request = self.request
    if request.method == 'GET' or request.method == 'DELETE':
      if 'username' in request.GET :
        username = request.GET['username']
      if 'access_token' in request.GET :
        access_token = request.GET['access_token']
    else :
      if 'username' in request.data :
        username = request.data['username']
      if 'access_token' in request.data :
        access_token = request.data['access_token']

    if username == '' or access_token == '' :
      raise PermissionDenied

    token = AccessToken.objects.filter(username = username)

    if len(token) == 0 or token[0].token != sha512(access_token) :
      # Validate access token with Steemconnect
      c = Client(access_token = access_token)

      try: 
        user = c.me()
      except:
        return HttpResponse(status=503)

      if user['user'] != username :
        # Wrong username / access_token pair
        raise PermissionDenied

      if len(token) == 0 :
        token = AccessToken(username = username,
                            token = sha512(access_token))
        token.save()
      else :
        # Access token was updated
        token.update(token = sha512(access_token))

    # User is valid, do we need to create a new SteemUser object?
    users = SteemUser.objects.filter(username = username)
    if len(users) == 0 :
      user = SteemUser(username = username)
      user.save()
    else :
      user = users[0]

    kwargs['user'] = user

    return func(self, *args, **kwargs)
  return wrapper

class BaseManageView(APIView):
  def dispatch(self, request, *args, **kwargs):
    if not hasattr(self, 'VIEWS_BY_METHOD'):
      raise Exception('VIEWS_BY_METHOD static dictionary variable must be defined on a ManageView class!')
    if request.method in self.VIEWS_BY_METHOD:
      return self.VIEWS_BY_METHOD[request.method]()(request, *args, **kwargs)

    return super().dispatch(request, *args, **kwargs)

class SteemUserView (APIView) :
  @csrf_exempt
  @check_user
  def get (self, request, format=None) :
    if request.method == 'GET':
      users = SteemUser.objects.all()
      serializer = SteemUserSerializer(users, many = True)
      return JsonResponse(serializer.data, safe=False)
    else :
        return HttpResponse(status=405)

class ConfigGetList (generics.ListAPIView) :
  queryset = Config.objects.all()
  serializer_class = ConfigSerializer

class ScraperGetList (generics.ListAPIView) :
  queryset = Scraper.objects.all()
  serializer_class = ScraperSerializer

class ScraperPatch (generics.UpdateAPIView) :
  queryset = Scraper.objects.all()
  serializer_class = ScraperSerializer

  def patch (self, request, pk, format = None, **kwargs) :
    scraper = Scraper.objects.get(pk = pk)
    serializer = ScraperSerializer(scraper, data = request.data)
    if serializer.is_valid() :
      serializer.save()
      return HttpResponse(status=200)
    else :
      return HttpResponse(status=400)

class ScraperList (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': ScraperGetList.as_view,
  }

class ScraperItem (BaseManageView) :
  VIEWS_BY_METHOD = {
    'PATCH': ScraperPatch.as_view,
  }

#class ScraperView (APIView) :
#  def get_scrapers (request = None) :
#    scrapers = Scraper.objects.all()
#
#    if request is not None :
#      allowed_filters = ['id']
#      for f in allowed_filters:
#        if f in request.query_params :
#          scrapers = scrapers.filter(**{f: request.query_params[f]})
#
#    return scrapers
#
#  @csrf_exempt
#  def get (self, request, format=None) :
#    scrapers = Scraper.objects.all()
#    serializer = ScraperSerializer(scrapers[0])
#    return JsonResponse(serializer.data, safe = False)
#
#  @csrf_exempt
#  def post (self, request, format=None) :
#    scrapers = ScraperView.get_scrapers(request)
#    if len(scrapers) == 0 :
#      return HttpResponse(status=404)
#    serializer = ScraperSerializer(scrapers[0], data = request.data)
#    if serializer.is_valid() :
#      serializer.save()
#      return HttpResponse(status=200)
#    else :
#      return HttpResponse(status=400)

class FavouriteTopicList (generics.ListAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def get_queryset (self, user = None) :
    return FavouriteTopic.objects.filter(user = user)

class FavouriteTopicDetails (generics.CreateAPIView,
                             generics.DestroyAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def delete (self, request, *args, **kwargs) :
    return self.destroy(request, *args, **kwargs)

class FavouriteTopicGetList (generics.ListAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def get_queryset (self, *args, **kwargs) :
    return FavouriteTopic.objects.filter(user = kwargs['user'].id) 

class FavouriteTopicGetDetails (generics.RetrieveAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def get_queryset (self, *args, **kwargs) :
    return FavouriteTopic.objects.filter(user = kwargs['user'].id) 

class FavouriteTopicPost (generics.CreateAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def post (self, request, *args, **kwargs) :
    request.data['user'] = kwargs['user'].id
    return self.create(request, *args, **kwargs)

class FavouriteTopicDelete (generics.DestroyAPIView):
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def delete (self, request, pk, format = None, **kwargs) :
    topic = FavouriteTopic.objects.get(pk = pk)
    if topic.user.id == kwargs['user'].id :
      topic.delete()
      return HttpResponse(status=204)
    else :
      return HttpResponse(status=403)

class ConfigList (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': ConfigGetList.as_view
  }

class HelpView (generics.ListAPIView) :
  serializer_class = HelpSerializer
  allowed_filters = ['lang']

  def get_queryset (self) :
    queryset = Help.objects.all()
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    return queryset

class FavouriteTopicList (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': FavouriteTopicGetList.as_view,
    'POST': FavouriteTopicPost.as_view,
  }

class FavouriteTopicItem (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': FavouriteTopicGetDetails.as_view,
    'DELETE': FavouriteTopicDelete.as_view,
  }

def favourite_topic (request, user = None):
  if request.method == 'GET':
    topics = FavouriteTopic.objects.filter(user = user)
    serializer = FavouriteTopicSerializer(topics, many = True)
    return JsonResponse(serializer.data, safe = False)
  elif request.method == 'POST':
    # First check if user has already subscribed to this topic
    topics = FavouriteTopic.objects.filter(user = user,
      topic_id = request.data['topic'])
    if len(topics) != 0 :
      return HttpResponse(status=400)

    topic = FavouriteTopic.objects.create(user = user,
      topic_id = request.data['topic'])
    serializer = FavouriteTopicSerializer(topic)
    return JsonResponse(serializer.data, safe=False)
  elif request.method == 'DELETE' :
    topics = FavouriteTopic.objects.filter(user = user,
      topic_id = request.GET['topic'])
    if len(topics) == 0 :
      return HttpResponse(status=404)
    topics[0].delete()
    return HttpResponse(status=200)
  else :
      return HttpResponse(status=405)

@csrf_exempt
@api_view(['GET'])
def topic (request) :
  if request.method == 'GET':
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many = True)
    return JsonResponse(serializer.data, safe = False)
  else :
    return HttpResponse(status=405)

class QuestionFilter (rest_framework.FilterSet) :
    created_gte = django_filters.IsoDateTimeFilter(
      field_name = 'created',
      lookup_expr = 'gte')

    class Meta :
      model = Question
      fields = ('author', 'created_gte', 'topic', 'answer_count')

class QuestionView (generics.ListAPIView,
                    generics.CreateAPIView,
                    generics.UpdateAPIView) :
  serializer_class = QuestionSerializer
  filter_backends = (OrderingFilter,)
  ordering_fields = ('created', 'active', 'total_payout_value', 'author_payout_value', 'net_votes', 'answer_count')
  allowed_filters = ['id', 'author', 'permlink', 'topic', 'answer_count']
  #filter_backends = (rest_framework.DjangoFilterBackend, OrderingFilter,)
  filter_class = QuestionFilter
  queryset = Question.objects.filter(flagged = False)

  def get_queryset (self) :
    queryset = Question.objects.filter(flagged = False)
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    return queryset

  def get_object (self) :
    queryset = Question.objects.filter(flagged = False)
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    if len(queryset) :
      obj = queryset[0]
      self.check_object_permissions(self.request, obj)
    else :
      if 'topic' not in self.request.data :
        topic = QuestionSerializer.find_topic((self.request.data.get('tag1', None),
          self.request.data.get('tag2', None),
          self.request.data.get('tag3', None),
          self.request.data.get('tag4', None),
          self.request.data.get('tag5', None)))
        if topic is None :
          return None
        self.request.data['topic'] = topic.id
      serializer = QuestionSerializer(data = self.request.data)
      if serializer.is_valid() :
        obj = serializer.save()
      else :
        obj = None

    return obj

  def put(self, request, *args, **kwargs) :
    if 'topic' not in request.data :
      topic = QuestionSerializer.find_topic((request.data.get('tag1', None),
        request.data.get('tag2', None),
        request.data.get('tag3', None),
        request.data.get('tag4', None),
        request.data.get('tag5', None)))
      if topic is not None :
        request.data['topic'] = topic.id
    return self.partial_update(request, args, kwargs)


@csrf_exempt
@api_view(['GET'])
def question_count (request) :
  return JsonResponse({
    'count': len(get_questions(request))
  }, 
  safe = False)

class FavouriteTopicPost (generics.CreateAPIView) :
  queryset = FavouriteTopic.objects.all()
  serializer_class = FavouriteTopicSerializer

  @check_user
  def post (self, request, *args, **kwargs) :
    request.data['user'] = kwargs['user'].id
    return self.create(request, *args, **kwargs)

class AnswerFilter (rest_framework.FilterSet) :
    created_gte = django_filters.IsoDateTimeFilter(
      field_name = 'created',
      lookup_expr = 'gte')

    class Meta :
      model = Answer
      fields = ('created_gte', 'question_id', 'author')

class AnswerView (generics.ListAPIView,
                    generics.CreateAPIView,
                    generics.UpdateAPIView) :
  serializer_class = AnswerSerializer
  ordering_fields = ('created', 'total_payout_value', 'author_payout_value', 'net_votes', 'active',)
  filter_class = AnswerFilter
  filter_backends = (rest_framework.DjangoFilterBackend, OrderingFilter,)
  queryset = Answer.objects.filter(flagged = False)
  allowed_filters = ['id', 'question', 'author', 'permlink']

  def get_queryset (self) :
    queryset = Answer.objects.filter(flagged = False)
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    return queryset

  def get_object (self) :
    queryset = Answer.objects.filter(flagged = False)
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    if len(queryset) :
      obj = queryset[0]
      self.check_object_permissions(self.request, obj)
    else :
      serializer = AnswerSerializer(data = self.request.data)
      if serializer.is_valid() :
        obj = serializer.save()
      else :
        obj = None

    return obj

  def put(self, request, *args, **kwargs) :
    return self.partial_update(request, args, kwargs)


@csrf_exempt
@api_view(['GET'])
def answer_count (request) :
  return JsonResponse({
    'count': len(get_answers(request))
  }, 
  safe = False)

class QuestionGetDetails (generics.RetrieveAPIView) :
  queryset = Question.objects.all()
  serializer_class = QuestionSerializer
  allowed_filters = ['id', 'author', 'permlink', 'topic', 'answer_count']



class QuestionItem (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': QuestionGetDetails.as_view,
  }

class NewQuestion (generics.CreateAPIView) :
  @check_user
  def post (self, request, *args, **kwargs) :
    if 'permlink' not in request.data or \
        'tags' not in request.data or \
        'title' not in request.data :
      return HttpResponse(status=400)

    topic = QuestionSerializer.find_topic(request.data['tags'])

    if topic is None :
      return HttpResponse(status=400)

    now = datetime.now()
    question = Question(created = now,
      author = kwargs['user'].username,
      title = request.data['title'],
      permlink = request.data['permlink'],
      active = now,
      tag1 = request.data['tags'][0] if len(request.data['tags']) >= 1 else None,
      tag2 = request.data['tags'][1] if len(request.data['tags']) >= 2 else None,
      tag3 = request.data['tags'][2] if len(request.data['tags']) >= 3 else None,
      tag4 = request.data['tags'][3] if len(request.data['tags']) >= 4 else None,
      tag5 = request.data['tags'][4] if len(request.data['tags']) >= 5 else None,
      topic = topic)
    question.save()
    return HttpResponse(status=204)

class NewAnswer (generics.CreateAPIView) :
  @check_user
  def post (self, request, *args, **kwargs) :
    if 'permlink' not in request.data or \
        'question_author' not in request.data or \
        'question_permlink' not in request.data or \
        'tags' not in request.data or \
        'title' not in request.data :
      return HttpResponse(status=400)

    answers = Answer.objects.filter(author = kwargs['user'].username).filter(question__permlink = request.data['question_permlink']).filter(question__author = request.data['question_author'])

    if len(answers) != 0 :
        return HttpResponse(status=400) # User already answered this question

    questions = Question.objects.filter(permlink = request.data['question_permlink']).filter(author = request.data['question_author'])
    if len(questions) == 0 :
        return HttpResponse(status=400)

    now = datetime.now()
    answer = Answer(question = questions[0],
      created = now,
      author = kwargs['user'].username,
      title = request.data['title'],
      permlink = request.data['permlink'],
      active = now,
      tag1 = request.data['tags'][0] if len(request.data['tags']) >= 1 else None,
      tag2 = request.data['tags'][1] if len(request.data['tags']) >= 2 else None,
      tag3 = request.data['tags'][2] if len(request.data['tags']) >= 3 else None,
      tag4 = request.data['tags'][3] if len(request.data['tags']) >= 4 else None,
      tag5 = request.data['tags'][4] if len(request.data['tags']) >= 5 else None)
    answer.save()
    return HttpResponse(status=204)

class BookmarkList (generics.ListAPIView) :
  queryset = Bookmark.objects.all()
  serializer_class = BookmarkSerializer

  @check_user
  def get_queryset (self, user = None) :
    return Bookmark.objects.filter(user = user)

class BookmarkPost (generics.CreateAPIView) :
  queryset = Bookmark.objects.all()
  serializer_class = BookmarkSerializer

  @check_user
  def post (self, request, *args, **kwargs) :
    request.data['user'] = kwargs['user'].id
    return self.create(request, *args, **kwargs)

class BookmarkDelete (generics.DestroyAPIView):
  queryset = Bookmark.objects.all()
  serializer_class = BookmarkSerializer

  @check_user
  def delete (self, request, pk, format = None, **kwargs) :
    bookmark = Bookmark.objects.get(pk = pk)
    if bookmark.user.id == kwargs['user'].id :
      bookmark.delete()
      return HttpResponse(status=204)
    else :
      return HttpResponse(status=403)

class BookmarkList (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': BookmarkList.as_view,
    'POST': BookmarkPost.as_view,
  }

class BookmarkGetDetails (generics.RetrieveAPIView) :
  queryset = Bookmark.objects.all()
  serializer_class = BookmarkSerializer

  @check_user
  def get_queryset (self, *args, **kwargs) :
    return Bookmark.objects.filter(user = kwargs['user'].id) 

class BookmarkItem (BaseManageView) :
  VIEWS_BY_METHOD = {
    'GET': BookmarkGetDetails.as_view,
    'DELETE': BookmarkDelete.as_view,
  }
