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

class QuestionSerializer (serializers.ModelSerializer) :

  def find_topic (tags) :
    main_tag = Config.objects.all()[0].tag
    main_tag_found = False
    topic = None
    for tag in tags :
      if main_tag_found is False and tag == main_tag :
        main_tag_found = True
      elif topic is None :
        topics = Topic.objects.filter(topic__iexact = tag)
        if len(topics) > 0 :
          topic = topics[0]
    return topic

  def validate_title(self, value) :
    value = value.strip()
    if value[-1] != '?' :
      raise serializers.ValidationError('Question must finish with question mark')
    return value

  class Meta :
    model = Question
    fields = '__all__'

class AnswerSerializer (serializers.ModelSerializer) :
  def validate_title(self, value) :
    value = value.strip()
    if value[-1] != '?' :
      raise serializers.ValidationError('Answer must finish with answer mark')
    return value

  class Meta :
    model = Answer
    fields = '__all__'
