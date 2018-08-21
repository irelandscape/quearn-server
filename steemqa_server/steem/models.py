from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

class Config (models.Model) :
  tag = models.CharField (
    help_text = 'The main SteemQA application tag',
    max_length = 40)

class Scraper (models.Model) :
  nodes = models.TextField (
    help_text = 'The steem nodes to use (in order of priority)',
    default = 'gtg.steem.house:8090,steemd.minnowsupportproject.org,steemd.privex.io,steemd.steemgigs.org,steemd.steemit.com,rpc.curiesteem.com,rpc.steemliberator.com,rpc.steemviz.com')

  oldest_author = models.TextField (
    blank = True,
    null = True)

  oldest_permlink = models.TextField (
    blank = True,
    null = True)


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
    help_text = 'SHA-512 encrypted version of Steemconnect access token',
    max_length = 160,
    db_index = True)

  class Meta:
    ordering = ('username',)


class Topic (models.Model) :
  topic = models.CharField(
    max_length = 80,
    unique = True,
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

  def __str__ (self) :
    return self.topic

  class Meta :
    ordering = ('topic', )

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

