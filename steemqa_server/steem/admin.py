from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Config)
admin.site.register(Scraper)
admin.site.register(SteemUser)
admin.site.register(Topic)
admin.site.register(FavouriteTopic)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Bookmark)
