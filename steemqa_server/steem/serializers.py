from rest_framework import serializers
from steem.models import *

class ConfigSerializer (serializers.ModelSerializer) :
  class Meta :
    model = Config
    fields = '__all__'

class ScraperSerializer (serializers.ModelSerializer) :
  class Meta :
    model = Scraper
    fields = '__all__'

class SteemUserSerializer (serializers.ModelSerializer) :
  class Meta :
    model = SteemUser
    fields = '__all__'

class TopicSerializer (serializers.ModelSerializer) :
  class Meta :
    model = Topic
    fields = '__all__'

class FavouriteTopicSerializer (serializers.ModelSerializer) :
  class Meta :
    model = FavouriteTopic
    fields = '__all__'

