from django.db import models
from django.conf import settings

class ContentPriority(models.IntegerChoices):
    LOW = 0, 'Low'
    NORMAL = 1, 'Normal'
    HIGH = 2, 'High'

class Import(models.Model):
    service = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    profile = models.CharField(null=True, blank=True, max_length=100)

class Content(models.Model):
    title = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    genre = models.CharField(null=True, blank=True, max_length=100)
    runtime = models.CharField(max_length=50, null=True, blank=True)
    episodes = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    content_type = models.CharField(null=True, blank=True, max_length=100)
    priority = models.IntegerField(default=ContentPriority.NORMAL, choices=ContentPriority.choices)
    
    def __str__(self):
        return f"{self.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shows = models.ManyToManyField(Content)
    
    def __str__(self):
        return f"{self.user}'s watchlist"