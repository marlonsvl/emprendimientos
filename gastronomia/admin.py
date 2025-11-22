from django.contrib import admin
from .models import Establecimiento, Like, Rating, Comment, UserProfile


# Register your models here.
admin.site.register(Establecimiento)
admin.site.register(Like)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(UserProfile)
