from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from steem.models import Answer, Question, Topic

#@receiver(post_save, sender = Question)
#def question_post_save(sender, **kwargs) :
#  if not kwargs['created'] :
#    return
#  question = kwargs['instance']
#  topic = Topic.objects.get(pk = question.topic_id)
#  topic.question_count += 1
#  topic.save(update_fields = ['question_count'])
#
#@receiver(post_delete, sender = Question)
#def question_post_delete(sender, **kwargs) :
#  if not kwargs['created'] :
#    return
#  question = kwargs['instance']
#  topic = Topic.objects.get(pk = question.topic_id)
#  if topic.question_count > 0 :
#      topic.question_count -= 1
#      topic.save(update_fields = ['question_count'])

@receiver(post_save, sender = Answer)
def answer_post_save(sender, **kwargs) :
  if not kwargs['created'] :
    return
  answer = kwargs['instance']
  question = Question.objects.get(pk = answer.question_id)
  if question.answer_count is None :
    question.answer_count = 0
  question.answer_count += 1
  question.save(update_fields = ['answer_count'])

@receiver(post_delete, sender = Answer)
def answer_post_delete(sender, **kwargs) :
  answer = kwargs['instance']
  question = Question.objects.get(pk = answer.question_id)
  if question.answer_count is not None :
    question.answer_count -= 1
    question.save(update_fields = ['answer_count'])
