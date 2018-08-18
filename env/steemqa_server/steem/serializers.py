from rest_framework import serializers
from steem.models import *

class SteemUserSerializer (serializers.ModelSerializer) :
  class Meta :
    model = SteemUser
    fields = ('id',
      'created',
      'username',
    )

class TopicSerializer (serializers.ModelSerializer) :
  class Meta :
    model = Topic
    fields = '__all__'

class FavouriteTopicSerializer (serializers.ModelSerializer) :
    model = FavouriteTopic
    fields = '__all__'

