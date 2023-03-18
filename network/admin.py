from django.contrib import admin
from .models import User, Post, Liked, Followed
# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Liked)
admin.site.register(Followed)