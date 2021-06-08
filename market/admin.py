from django.contrib import admin

from .models import Market, Trader, Trade, RoundStat

class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_id', 'round', 'alpha', 'beta', 'theta', 'min_cost', 'max_cost', 'created_at')
    readonly_fields = ['market_id']

class TraderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'market', 'prod_cost', 'created_at')

class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'trader', 'unit_price', 'unit_amount', 'round', 'was_forced', 'profit', 'balance_after', 'units_sold', 'created_at')


class RoundStatAdmin(admin.ModelAdmin):
    list_display = ('market', 'round', 'avg_price')

admin.site.register(Market, MarketAdmin)
admin.site.register(Trader, TraderAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(RoundStat, RoundStatAdmin)
