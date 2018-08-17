from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from steem.models import SteemUser
from steem.serializers import SteemUserSerializer
from steemconnect.client import Client
from steem.config import CLIENT_ID, CLIENT_SECRET

def check_user (request) :
  def decorator (func) :
    def wrapper (*args, **kwargs) :
      username = ''
      access_token = ''
      if request.method == 'GET' and 'username' in request.GET :
        username = request.GET['username']
        access_token = request.GET['access_token']
      if request.method == 'POST' and 'username' in request.POST :
        username = request.POST['username']
        access_token = request.POST['access_token']
      if request.method == 'PATCH' and 'username' in request.PATCH :
        username = request.PATCH['username']
        access_token = request.PATCH['access_token']
      if request.method == 'DELETE' and 'username' in request.DELETE :
        username = request.DELETE['username']
        access_token = request.DELETE['access_token']

      if username == '' or access_token == '' :
        return HttpResponse(status=403)

      token = AccessToken.objects.filter(username = username)
      
      if len(token)  == 0 or token.access_token != access_token :
        # Validate access token with Steemconnect
        c = Client(
          client_id = CLIENT_ID,
          client_secret = CLIENT_SECRET)

        try: 
          user = c.me()
        except:
          return HttpResponse(status=503)

        if user.username != username :
          # Wrong username / access_token pair
          return HttpResponse(status=403)

        if len(token) == 0 :
          token = AccessToken(username = username,
                              access_token = access_token)
          token.save()
        else :
          # Access token was updated
          token[0].update(access_token = access_token)

      func(*args, **kwargs)
    return wrapper
  return decorator

# Create your views here.
@csrf_exempt
@check_user('request')
def api_steemusers (request, user_valid = False) :
  if request.method == 'GET':
    users = SteemUser.objects.all()
    serializer = SteemUserSerializer(users, many = True)
    return JsonResponse(serializer.data, safe=False)
  else :
      return HttpResponse(status=405)


@csrf_exempt
def api_steemuser_details (request, pk):
  try:
    user = SteemUser.objects.get(pk=pk)
  except SteemUser.DoesNotExist:
      return HttpResponse(status=404)

  if request.method == 'GET':
      serializer = SteemUserSerializer(user)
      return JsonResponse(serializer.data)
  else :
      return HttpResponse(status=405)
