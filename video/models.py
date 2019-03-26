from django.db import models
import datetime
from django.utils import timezone


class Movie(models.Model):
    movieid = models.CharField(max_length=140)
    playcount = models.FloatField(null=True)
    title = models.CharField(max_length=600, null=True)
    posted_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    remove = models.NullBooleanField(default=False)
    userid = models.CharField(max_length=140, default=None, null=True)
    filetype = models.CharField(max_length=140, default='unknown', null=True)

class AccessLog(models.Model):
    movieid = models.CharField(max_length=140, null=True, default=None)
    at = models.DateTimeField(auto_now_add=True, null=True)
    userid = models.CharField(max_length=140, default=None, null=True)
