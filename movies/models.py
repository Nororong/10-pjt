from django.db import models
from accounts.models import User

class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=255)
    character = models.CharField(max_length=255, null=True, blank=True)
    profile_path = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} as {self.character}"

class Movie(models.Model):
    like_users = models.ManyToManyField(User, related_name='like_movies')
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    runtime = models.IntegerField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    actors = models.ManyToManyField(Actor, related_name="movies")


    def __str__(self):
        return self.title
