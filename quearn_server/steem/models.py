from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

MAX_TAG_LENGTH = 40

class Config (models.Model) :
  appName = models.CharField (
    max_length = 40,
    blank = True,
    null = True)

  tag = models.CharField (
    help_text = 'The main SteemQA application tag',
    max_length = MAX_TAG_LENGTH)

  carousel_slide_count = models.PositiveIntegerField (
    help_text = 'The number of questions to load in the home page carousel',
    default = 5,
    blank = True,
    null = True)

  carousel_history = models.PositiveIntegerField (
    help_text = 'Time period (in days) to report top questions in carousel',
    default = 7,
    blank = True,
    null = True)

  initial_slides_count = models.PositiveIntegerField (
    help_text = 'Number of initial slides to load in a slide swiper',
    default = 10,
    blank = True,
    null = True)
  new_slides_count = models.PositiveIntegerField (
    help_text = 'Number of slides to load in the background when reaching the end of a slide swiper',
    default = 3,
    blank = True,
    null = True)
  initial_grid_batch_size = models.PositiveIntegerField (
    help_text = 'Number of elements to load into a card grid',
    default = 20,
    blank = True,
    null = True)

class Scraper (models.Model) :
  nodes = models.TextField (
    help_text = 'The steem nodes to use (in order of priority)',
    default = 'api.steemit.com,steemd.minnowsupportproject.org,steemd.privex.io,steemd.steemgigs.org,steemd.steemit.com,rpc.curiesteem.com,rpc.steemliberator.com,rpc.steemviz.com')

  block_nbr = models.PositiveIntegerField (
    blank = True,
    null = True)


class SteemUser (models.Model) :
  created = models.DateTimeField(auto_now_add=True)

  username = models.CharField(
    max_length = 40,
    db_index = True)

  class Meta:
    ordering = ('username',)

  def __str__ (self) :
    return self.username

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
    max_length = 40,
    unique = True,
    db_index = True)

  parent = models.ForeignKey(
    'self',
    related_name = 'parent_topic',
    on_delete=models.CASCADE,
    blank = True,
    null = True)

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

  title = models.CharField (
    max_length = 128,
    db_index = True)

  permlink = models.CharField(
    max_length = 160,
    db_index = True)

  active = models.DateTimeField(
    help_text = 'The last time this content was “touched” by voting or reply',
    blank = True,
    null = True)

  # Must have at the main tag. Questions must also have a second tag for the topic
  tag1 = models.CharField (
    max_length = MAX_TAG_LENGTH)

  tag2 = models.CharField (
    max_length = MAX_TAG_LENGTH,
    blank = True,
    null = True)

  tag3 = models.CharField (
    max_length = MAX_TAG_LENGTH,
    blank = True,
    null = True)

  tag4 = models.CharField (
    max_length = MAX_TAG_LENGTH,
    blank = True,
    null = True)

  tag5 = models.CharField (
    max_length = MAX_TAG_LENGTH,
    blank = True,
    null = True)

  flagged = models.BooleanField (
    help_text = 'Indicates if this item has been flagged by moderators',
    default = False)

  net_votes = models.PositiveIntegerField (
    help_text = 'Net positive votes',
    default = 0)

  author_payout_value = models.FloatField (
    help_text = 'Tracks the total payout (in SBD) this content has received over time',
    default = 0)

  class Meta :
    abstract = True

  def __str__ (self) :
    return self.title

class Question (Discussion) :
  topic = models.ForeignKey(
    Topic,
    on_delete=models.CASCADE)

  answer_count = models.PositiveIntegerField (
    default = 0,
    blank = True,
    null = True)

class Answer (Discussion) :
  question = models.ForeignKey(
    Question,
    on_delete=models.CASCADE)

class Bookmark (models.Model) :
  user = models.ForeignKey(SteemUser,
    on_delete=models.CASCADE)

  question = models.ForeignKey(Question,
    on_delete=models.CASCADE)
