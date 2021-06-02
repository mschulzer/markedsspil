from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('join/', views.join, name='join'),
    path('create/', views.create, name='create'),
    path('<market_id>/play/', views.play, name='play'),
    path('<market_id>/wait/', views.wait, name='wait'),
    path('<market_id>/monitor/', views.monitor, name='monitor'),

    # APIs
    path('<market_id>/current-round/', views.current_round, name='current_round'),
    path('<market_id>/trader-api/', views.trader_api, name='trader_api'),
    #path('<market_id>/download/', views.download, name='download'),
]
