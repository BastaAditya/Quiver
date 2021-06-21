from django.contrib import admin
from .models import Comment, Post, Like, FriendRequest

# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(FriendRequest)
