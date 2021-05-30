"""
Helper functions used by the views
"""

from .models import Market, Trader, Trade


def create_forced_trade(trader, round_num, balance_after = None, profit = None):
    forced_trade = Trade.objects.create(
        round=round_num, # note that round num has to be speficied when creating a forced trade
        trader=trader,
        unit_price=0,
        unit_amount=0,
        balance_after = balance_after,
        profit = profit,
        was_forced=True
    )
    return forced_trade
