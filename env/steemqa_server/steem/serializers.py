from rest_framework import serializers
from steem.models import SteemUser, LANGUAGE_CHOICES, STYLE_CHOICES

class SteemUserSerializer (serializers.ModelSerializer) :
  class Meta :
    model = SteemUser
    fields = ('id',
      'created',
      'username',
    )

