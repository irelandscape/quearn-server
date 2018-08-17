from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from steem.models import Question, Topic

@receiver(post_save, sender = Question)
def question_post_save(sender, **kwargs) :
  question = kwargs['instance']
  topic = Topic.objects.get(pk = question.id)
  topic.update(question_count = topic.question_count + 1)

@receiver(post_delete, sender = Question)
def question_post_delete(sender, **kwargs) :
  question = kwargs['instance']
  topic = Topic.objects.get(pk = question.id)
  topic.update(question_count = topic.question_count - 1)
