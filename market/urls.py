from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    
    # Pages
    path('', views.home, name='home'),
    path('join/', views.join, name='join'),
    path('create/', views.create, name='create'),
    path('play/', views.play, name='play'),
    path('<market_id>/monitor/', views.monitor, name='monitor'),
    path('<market_id>/monitor/trader-table/', views.trader_table, name='trader_table'),
    path('<market_id>/market_edit/', views.market_edit, name='market_edit'),
    path('<market_id>/game_over_view/', views.game_over_view, name='game_over'),
    path('my_markets/', views.my_markets, name='my_markets'),

    # APIs
    path('<market_id>/current-round/', views.current_round, name='current_round'),
    #path('<market_id>/download/', views.download, name='download'),
]
