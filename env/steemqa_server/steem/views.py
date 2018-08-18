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
    if request.method == 'GET' and 'username' in request.GET and 'access_token' in request.GET :
      username = request.GET['username']
      access_token = request.GET['access_token']
    if request.method == 'POST' and 'username' in request.POST and 'access_token' in request.POST :
      username = request.POST['username']
      access_token = request.POST['access_token']
    if request.method == 'PATCH' and 'username' in request.PATCH and 'access_token' in request.PATCH :
      username = request.PATCH['username']
      access_token = request.PATCH['access_token']
    if request.method == 'DELETE' and 'username' in request.DELETE and 'access_token' in request.DELETE :
      username = request.DELETE['username']
      access_token = request.DELETE['access_token']

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
