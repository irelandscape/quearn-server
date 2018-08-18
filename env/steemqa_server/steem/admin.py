from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SteemUser)
admin.site.register(Topic)
admin.site.register(FavouriteTopic)
