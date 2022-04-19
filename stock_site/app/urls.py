from django.urls import path
from . import views


urlpatterns = [
    path('watchlist', views.watchlist, name='watchlist'),
    path('<str:ticker_id>', views.ticker_view, name='ticker'), #Grabs the ticker input
    path('', views.index_view, name='index'),
    path('accounts/register', views.register, name='register'),
    path('delete/<stock_id>', views.delete, name='delete'),
    path('stop/please_login', views.login_please, name='please_login')
]