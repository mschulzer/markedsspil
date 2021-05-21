from django.contrib import admin

from .models import Market, Trader, Trade, Stats

class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_id', 'round', 'alpha', 'beta', 'theta', 'min_cost', 'max_cost', 'created_at')


class TraderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'market', 'money', 'prod_cost')


class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'trader', 'unit_price', 'unit_amount', 'round')


class StatsAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'trader',
                    'round', 'price', 'amount', 'profit', 'bank')

admin.site.register(Market, MarketAdmin)
admin.site.register(Trader, TraderAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Stats, StatsAdmin)
