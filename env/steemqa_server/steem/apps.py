from django.apps import AppConfig


class SteemConfig(AppConfig):
    name = 'steem'
    verbose_name = 'Steem Application'

    def ready (self) :
      import steem.signals
