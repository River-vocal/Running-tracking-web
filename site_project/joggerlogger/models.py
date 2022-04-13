from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class Account(models.Model):
    bio = models.CharField(max_length=200)
    picture = models.FileField(blank=True, default="default.png")
    content_type = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name="account")
    goal = models.CharField(max_length=200)

class Run(models.Model):
    runner = models.ForeignKey(Account, models.PROTECT, related_name="runs")
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    distance = models.FloatField()
    duration = models.FloatField()  # Duration in minutes
    date = models.DateField()
    is_at_meet = models.BooleanField()
    lat_longs = models.JSONField(default = list)
    created_by = models.ForeignKey(User, models.PROTECT)
    created_at = models.DateTimeField()


class Meet(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    date = models.DateField()

    runs = models.ForeignKey(Run, models.PROTECT, related_name="meet")

    created_by = models.ForeignKey(User, models.PROTECT)
    created_at = models.DateTimeField()


class Team(models.Model):
    name = models.CharField(max_length=200)
    slogan = models.CharField(max_length=400)
    coach = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="coached_team")
    runners = models.ManyToManyField(Account, related_name="team")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_team")
    goal = models.CharField(max_length=200)

class Goal(models.Model):
    runner = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="runner_goal")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="team_goal")
    goal = models.CharField(max_length=200)