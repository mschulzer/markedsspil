from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    path('', views.index, name='index'),
    path('join', views.join, name='join'),
    path('<market_id>/play', views.play, name='play'),
    path('<market_id>/sell', views.sell, name='sell'),
]
