from django.contrib import admin
from .models import User, Comment, Reaction, Post, Topic, ReactionTypes,FrontStickyType, BadgeType,NotificationSubscribe, Notification,Badge

# Register your models here.

admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(ReactionTypes)
admin.site.register(FrontStickyType)
admin.site.register(BadgeType)
admin.site.register(NotificationSubscribe)
admin.site.register(Notification)
admin.site.register(Badge)
