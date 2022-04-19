import sqlite3

import django.contrib.messages
from django.shortcuts import render
from django import forms
from . import models
from .forms import TickerForm
from django.shortcuts import HttpResponseRedirect, redirect
import yfinance
import requests
from plotly import graph_objs as go
import json
import pandas as pd
from plotly.offline import plot
from django.shortcuts import redirect
from .models import Watchlist
from .forms import WatchlistForm
from . import models
from .models import Watchlist
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser


# Create your views here.


def index_view(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)


        if form.is_valid():                 #If Form is valid we will be brought to the page with the ticker information
            ticker = request.POST['ticker']
            return HttpResponseRedirect(ticker)
        else: #If form is not valid then we will
            context = {}
            not_valid = 'Not Valid Ticker, Try Again Please.'
            context['not_valid'] = not_valid
            django.contrib.messages.error(request, 'Invalid Form Submission')
            django.contrib.messages.error(request, form.errors)
    else:
        form = TickerForm()

    try:
        return render(request, 'app/index.html', {'form':form})
    except:
        return redirect('stock_site:index') #if ticker is not valid then we will stay at index.html which is /stocks



def ticker_view(request, ticker_id):


    context = {}
    context['ticker'] = ticker_id.upper()
    try:

        stock = yfinance.Ticker(f'{context["ticker"]}')

        #news = stock.info
        #sector = news['sector']
        #context['sector'] = sector


        querystring = {"symbol":f'{ticker_id}'} #Grabing the symbol that the user searched
        headers = {
            "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
            "X-RapidAPI-Key": "473e98d262mshdd6559848304f75p191f9fjsn08d74644bdf2"
        }

        response_market = requests.get(f"https://yh-finance.p.rapidapi.com/stock/v2/get-profile", headers=headers, params=querystring) #CONNECTING TO YH-FINANCE API To get data
        market_data = response_market.json()

    except:
        return redirect('/stocks')




    graph_data = stock.history('1y') #Download historical data for the ticker from yahoo finance
    graph_data.reset_index(inplace=True)
    fig = go.Figure(data=[go.Candlestick(x=graph_data['Date'], #Create a Candlestick chart based off the histroical data
                                        open=graph_data['Open'],
                                        high=graph_data['High'],
                                        low=graph_data['Low'],
                                        close=graph_data['Close'])])

    #chart = fig.show()
    #context['chart'] = chart


    plot_div = plot(fig, output_type='div', include_plotlyjs=False) #Plot the Yearly Chart using plotly.
    context['plot'] = plot_div

    try:

        #Stock Info Grabbing data from the dictionary
        current_price = market_data['price']['regularMarketPrice']['fmt']
        context['current_price'] = current_price


        todays_high = market_data['price']['regularMarketDayHigh']['fmt']
        context['todays_high'] = todays_high


        avg_daily_vol = market_data['price']['averageDailyVolume3Month']['fmt']
        context['avg_daily_vol'] = avg_daily_vol

        ten_day = market_data['price']['averageDailyVolume10Day']['fmt']
        context['ten_day'] = ten_day


        marketcap = market_data['price']['marketCap']['fmt']
        context['marketcap'] = marketcap


        current_vol = market_data['price']['regularMarketVolume']['fmt']
        context['current_vol'] = current_vol
    except:
        pass



    try:
        #Get-Statistics
        response_stats = requests.get(f"https://yh-finance.p.rapidapi.com/stock/v2/get-statistics", headers=headers,
                                       params=querystring)
        stats_data = response_stats.json()
        #More Stock Info from a different request address, grabbing the data from the dictionary



        fiftyweek = stats_data['defaultKeyStatistics']['52WeekChange']['fmt']
        context['fiftyweek'] = fiftyweek
        share_float = stats_data['defaultKeyStatistics']['floatShares']['fmt']
        context['share_float'] = share_float
        short_ratio = stats_data['defaultKeyStatistics']['shortRatio']['fmt']
        context['short_ratio'] = short_ratio
    except:
        pass


    #Grab news from Polygon API https://polygon.io/docs/stocks/get_v2_reference_news
    news_response = requests.get(f'https://api.polygon.io/v2/reference/news?ticker={ticker_id.upper()}&order=desc&limit=10&sort=published_utc&apiKey=HmhDgxJepK2LSHdNKHbi9qU92xrHMTvx')
    news_data = news_response.json()
    '''
    ARTICLES CLASS
    '''
    class Articles: #This class makes it easier for me to grab the data from the json without having to type more than I need too.
        def __init__(self, article_num):
            self.article_num = news_data['results'][article_num]
            self.title = news_data['results'][article_num]['title']
            self.author = news_data['results'][article_num]['author']
            self.day = news_data['results'][article_num]['published_utc'][0:10]
            self.url = news_data['results'][article_num]['article_url']
            self.image = news_data['results'][article_num]['image_url']
            self.desc = news_data['results'][article_num]['description']

    try:

        article_one = Articles(0)
        context['article_one'] = article_one
        article_two = Articles(1)
        context['article_two'] = article_two
        article_three = Articles(2)
        context['article_three'] = article_three
        article_four = Articles(3)
        context['article_four'] = article_four
        article_five = Articles(4)
        context['article_five'] = article_five
    except:
        pass


    try:
        debt_to_equity = stats_data['financialData']['debtToEquity']['fmt']
        context['debt_to_equity'] = debt_to_equity
        total_cash = stats_data['financialData']['totalCash']['fmt']
        context['total_cash'] = total_cash
        total_debt = stats_data['financialData']['totalDebt']['fmt']
        context['total_debt'] = total_debt
        total_revenue = stats_data['financialData']['totalRevenue']['fmt']
        context['total_revenue'] = total_revenue

    except:
        pass














    return render(request, 'app/ticker.html', context)

def watchlist(request):
    try:
        if request.method == 'POST':
            if request.user.is_authenticated():
                form = WatchlistForm(request.POST)






            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user #The field user will be automatically assigned to the current user logged in
                obj.save() #We will then save that data entry

                return redirect('watchlist')

    except:
        return redirect('watchlist')

    else:

        try:

            user = request.user   #Grabs the user request
            quotes = Watchlist.objects.filter(user=user) #Filter the watchlist model to user
            output = []

            for quote_item in quotes:
                querystring = {'symbol': f'{str(quote_item)}'}  # Fill in for ticker
                headers = {
                    "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
                    "X-RapidAPI-Key": "473e98d262mshdd6559848304f75p191f9fjsn08d74644bdf2"
                }
                api_request = requests.get('https://yh-finance.p.rapidapi.com/stock/v2/get-profile', params=querystring,
                                           headers=headers)

                try:
                    api = json.loads(api_request.content)  # Simillar to blank = blank.json() #Grap data from database
                    output.append(api)  # Everytime this loops it will save the output into the list output

                except Exception as e:
                    api = 'Error....'

        except:
            return redirect('please_login') #Returns user to login page please

    return render(request, 'app/watchlist.html', context={'quotes':quotes, 'output':output})


def register(request): #Used to register for site
    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
        return redirect('index')

    else:
        form = RegisterForm()

    return render(request, 'app/register.html', context={'form':form})

def delete(request, stock_id):
    try:

        item = Watchlist.objects.get(pk=stock_id)
        item.delete()
        return redirect(watchlist)
    except:
        pass


def login_please(request):
    return render(request, 'app/view.html')
