from django.contrib import admin

from .models import Market, Trader, Trade, Stats

admin.site.register(Market)
admin.site.register(Trader)
admin.site.register(Trade)
admin.site.register(Stats)
