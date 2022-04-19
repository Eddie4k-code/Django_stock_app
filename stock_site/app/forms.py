from django import forms
from django.forms import ModelForm
from .models import Watchlist
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import models
from django.contrib.auth.models import User



class TickerForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=5)

class WatchlistForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['ticker_name']



class RegisterForm(UserCreationForm):
    email = models.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

