from django.db import models

class SteemUser (models.Model) :
  created = models.DateTimeField(auto_now_add=True)
  username = models.CharField( max_length = 80)

  class Meta:
    ordering = ('username',)
