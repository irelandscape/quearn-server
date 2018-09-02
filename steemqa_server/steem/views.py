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
from steemqa_server.settings import STEEMCONNECT_CLIENT_ID
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics, filters
import json
import urllib
import dateparser
from beem import discussions
from datetime import datetime

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

class QuestionView (generics.ListAPIView,
                    generics.CreateAPIView,
                    generics.UpdateAPIView) :
  serializer_class = QuestionSerializer
  filter_backends = (filters.OrderingFilter,)
  ordering_fields = ('active',)
  allowed_filters = ['id', 'author', 'permlink']

  def get_queryset (self) :
    queryset = Question.objects.all()
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    return queryset

  def get_object (self) :
    queryset = Question.objects.all()
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
    return self.update(request, args, kwargs)


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

class AnswerView (generics.ListAPIView,
                    generics.CreateAPIView,
                    generics.UpdateAPIView) :
  serializer_class = AnswerSerializer
  filter_backends = (filters.OrderingFilter,)
  ordering_fields = ('active',)
  allowed_filters = ['id', 'author', 'permlink']

  def get_queryset (self) :
    queryset = Answer.objects.all()
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    return queryset

  def get_object (self) :
    queryset = Answer.objects.all()
    for f in self.allowed_filters:
      if f in self.request.query_params :
        queryset = queryset.filter(**{f: self.request.query_params[f]})

    if len(queryset) :
      obj = queryset[0]
      self.check_object_permissions(self.request, obj)
    else :
      if 'topic' not in self.request.data :
        topic = AnswerSerializer.find_topic((self.request.data.get('tag1', None),
          self.request.data.get('tag2', None),
          self.request.data.get('tag3', None),
          self.request.data.get('tag4', None),
          self.request.data.get('tag5', None)))
        if topic is None :
          return None
        self.request.data['topic'] = topic.id
      serializer = AnswerSerializer(data = self.request.data)
      if serializer.is_valid() :
        obj = serializer.save()
      else :
        obj = None

    return obj

  def put(self, request, *args, **kwargs) :
    if 'topic' not in request.data :
      print(request.data)
      topic = AnswerSerializer.find_topic((request.data.get('tag1', None),
        request.data.get('tag2', None),
        request.data.get('tag3', None),
        request.data.get('tag4', None),
        request.data.get('tag5', None)))
      if topic is not None :
        request.data['topic'] = topic.id
    return self.update(request, args, kwargs)


@csrf_exempt
@api_view(['GET'])
def answer_count (request) :
  return JsonResponse({
    'count': len(get_answers(request))
  }, 
  safe = False)


class NewQuestion (generics.CreateAPIView) :
  @check_user
  def post (self, request, *args, **kwargs) :
    if 'permlink' not in request.data :
      return HttpResponse(status=400)
    q = discussions.Query(limit = 1,
                          start_permlink = request.data['permlink'],
                          start_author = kwargs['user'].username,
                          tag = kwargs['user'].username)
    posts = discussions.Discussions_by_blog(q)
    post = posts[0]
    json = post.json()
    if len(post.json_metadata['tags']) > 1 :
      tag2 = post.json_metadata['tags'][1]
    else :
      tag2 = None
    if len(post.json_metadata['tags']) > 2 :
      tag3 = post.json_metadata['tags'][2]
    else :
      tag3 = None
    if len(post.json_metadata['tags']) > 3 :
      tag4 = post.json_metadata['tags'][3]
    else :
      tag4 = None
    if len(post.json_metadata['tags']) > 4 :
      tag5 = post.json_metadata['tags'][4]
    else :
      tag5 = None
    topic = QuestionSerializer.find_topic((post.json_metadata['tags'][0],
      tag2,
      tag3,
      tag4,
      tag5))

    if topic is None :
      return HttpResponse(status=400)

    question = Question(created = json['created'],
      author = post.author,
      title = post.title,
      permlink = post.permlink,
      active = dateparser.parse(json['active']),
      tag1 = post.json_metadata['tags'][0],
      tag2 = tag2,
      tag3 = tag3,
      tag4 = tag4,
      tag5 = tag5,
      net_votes = len(post.get_votes()),
      author_payout_value = post.get_author_rewards()['total_payout_SBD'].amount,
      topic = topic)
    question.save()
    return HttpResponse(status=204)
