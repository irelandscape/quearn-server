import hashlib
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from steem.models import *
from steem.serializers import *
from steemconnect.client import Client
from my_secrets.secrets import SECRET_KEY
from steemqa_server.settings import STEEMCONNECT_CLIENT_ID
from rest_framework.decorators import api_view

def sha512 (token) :
  hash = hashlib.sha512(token.encode('utf-8'))
  return hash.hexdigest()

def check_user (func) :
  def wrapper (*args, **kwargs) :
    username = ''
    access_token = ''
    request = args[0]
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
      return HttpResponse(status=403)

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
        return HttpResponse(status=403)

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

    return func(*args, **kwargs)
  return wrapper

# Create your views here.
@csrf_exempt
@check_user
def steemuser (request) :
  if request.method == 'GET':
    users = SteemUser.objects.all()
    serializer = SteemUserSerializer(users, many = True)
    return JsonResponse(serializer.data, safe=False)
  else :
      return HttpResponse(status=405)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@check_user
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
