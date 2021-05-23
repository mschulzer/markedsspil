from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    path('', views.home, name='home'),
    path('join/', views.join, name='join'),
    path('create/', views.create, name='create'),
    path('<market_id>/play/', views.play, name='play'),
    path('<market_id>/sell/', views.sell, name='sell'),
    path('<market_id>/wait/', views.wait, name='wait'),
    path('<market_id>/monitor/', views.monitor, name='monitor'),
    path('<market_id>/all_trades/', views.all_trades, name='all_trades'),
    path('<market_id>/current_round/', views.current_round, name='current_round'),
    path('<market_id>/traders_this_round/', views.traders_this_round, name='traders_this_round'),
    path('<market_id>/traders_in_market/', views.traders_in_market, name='traders_in_market'),
    path('<market_id>/download/', views.download, name='download'),
]
