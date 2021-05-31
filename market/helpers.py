"""
Helper functions used by the views
"""

from .models import Market, Trader, Trade


def create_forced_trade(trader, round_num):
    """
    Used in two different cases:
    1) To create fake trades for players who did not make a real trade in time in the current round
    2) To create fake trades for previous rounds for players who enters the game that has started
    """
    forced_trade = Trade.objects.create(
        round=round_num, # note that round num has to be speficied when creating a forced trade
        trader=trader,
        unit_price=None, 
        unit_amount=None,
        balance_after=None,
        profit = None,
        was_forced=True
    )
    return forced_trade
