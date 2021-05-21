from django.contrib import admin

from .models import Market, Trader, Trade, Stats


class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_id', 'round', 'alpha', 'beta', 'theta', 'min_cost', 'max_cost', 'created_at')

admin.site.register(Market, MarketAdmin)
admin.site.register(Trader)
admin.site.register(Trade)
admin.site.register(Stats)
