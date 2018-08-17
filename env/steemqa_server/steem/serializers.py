from rest_framework import serializers
from steem.models import SteemUser

class SteemUserSerializer (serializers.ModelSerializer) :
  class Meta :
    model = SteemUser
    fields = ('id',
      'created',
      'username',
    )

