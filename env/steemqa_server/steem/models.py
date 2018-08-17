from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

class SteemUser (models.Model) :
  created = models.DateTimeField(auto_now_add=True)

  username = models.CharField(
    max_length = 40,
    db_index = True)

  class Meta:
    ordering = ('username',)

class AccessToken (models.Model) :
  username = models.CharField(
    max_length = 40,
    db_index = True)

  token = models.CharField(
    max_length = 160,
    db_index = True)

  class Meta:
    ordering = ('username',)


class Topic (models.Model) :
  topic = models.CharField(
    max_length = 80,
    db_index = True)

  parent = models.ForeignKey(
    'self',
    related_name = 'parent_topic',
    on_delete=models.CASCADE,
    blank = True,
    null = True)

  question_count = models.PositiveIntegerField(
    help_text = 'The number of existing questions associated with this topics',
    default = 0)

class FavouriteTopic (models.Model) :
  user = models.ForeignKey(
    SteemUser,
    on_delete=models.CASCADE)

  topic = models.ForeignKey(
    Topic,
    on_delete=models.CASCADE)

class Discussion (models.Model) :
  created = models.DateTimeField(db_index = True)

  author = models.CharField(
    max_length = 40,
    db_index = True)

  permlink = models.CharField(
    max_length = 160,
    db_index = True)

  upvotes = models.PositiveIntegerField(
    default = 0,
    db_index = True)

  class Meta :
    abstract = True

class Question (Discussion) :
  topic = models.ForeignKey(
    Topic,
    on_delete=models.CASCADE)

class Answer (Discussion) :
  question = models.ForeignKey(
    Question,
    on_delete=models.CASCADE)

