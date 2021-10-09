from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [

    path('', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('<market_id>/play/', views.play, name='play'),
    path('<market_id>/monitor/', views.monitor, name='monitor'),
    path('<market_id>/market_edit/', views.market_edit, name='market_edit'),
    path('my_markets/', views.my_markets, name='my_markets'),

    path('<market_id>/finish_round', views.finish_round, name='finish_round'),
    path('remove_trader_from_market',
         views.remove_trader_from_market, name='remove_trader_from_market'),
    path('<market_id>/toggle_monitor_auto_pilot_setting/',
         views.toggle_monitor_auto_pilot_setting, name='toggle_monitor_auto_pilot_setting'),

    # htmx inclusion templates
    path('<market_id>/monitor/trader-table/',
         views.trader_table, name='trader_table'),

    # APIs
    path('<market_id>/current-round/', views.current_round, name='current_round'),
    #path('<market_id>/download/', views.download, name='download'),
]
