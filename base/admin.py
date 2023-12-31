from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message, User, Media, Notification, UserPreference

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Media)
admin.site.register(Notification)
admin.site.register(UserPreference)
