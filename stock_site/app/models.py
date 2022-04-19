from django.db import models
from django import forms
import requests
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class Watchlist(models.Model):
    ticker_name = models.CharField(max_length=5)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist", null=True)  # Allows each user to have a different watchlisty

    def __str__(self):
        return self.ticker_name

