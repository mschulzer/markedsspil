from django.contrib import admin

from .models import Market, Trader, Trade, RoundStat

class MarketAdmin(admin.ModelAdmin):
    list_display = (
        'market_id',
        'round',
        'alpha',
        'beta',
        'theta',
        'min_cost',
        'max_cost',
        'product_name_singular',
        'initial_balance',
        'max_rounds',
        'endless',
        'allow_robots',
        'created_by',
        'created_at')

    readonly_fields = ['market_id']

class TraderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'market',
        'prod_cost',
        'created_at',
        'balance',
        'round_joined',
        'auto_play'
    )

class TradeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'trader',
        'unit_price',
        'was_forced',
        'unit_amount',
        'round',
        'demand',
        'profit',
        'balance_before',
        'balance_after',
        'units_sold',
        'created_at'
    )

class RoundStatAdmin(admin.ModelAdmin):
    list_display = (
        'market',
        'round',
        'avg_price',
        'avg_balance_after',
        'avg_amount',
        'created_at'
    )

admin.site.register(Market, MarketAdmin)
admin.site.register(Trader, TraderAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(RoundStat, RoundStatAdmin)
