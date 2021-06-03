"""
Helper functions used by the views
"""

from .models import Market, Trader, Trade


def create_forced_trade(trader, round_num, is_new_trader):
    """
    Used in two different situations:
    1) To create fake trades for players who did not make a real trade in time in the current round
    2) To create fake trades for previous rounds for players who enters the game that has started
    """
    if is_new_trader:
        balance_after = None
    else: 
        balance_after = trader.balance
    forced_trade = Trade.objects.create(
        round=round_num, 
        trader=trader,
        unit_price=None, 
        unit_amount=None,
        balance_after=balance_after,
        profit = None,
        was_forced=True
    )
    return forced_trade

def get_trades(market, round="all_rounds"):
    trades_by_market = Trade.objects.filter(trader__in=Trader.objects.filter(market=market))
    if round == "all_rounds":
        return trades_by_market
    else:
        assert(type(round) == int)
        return trades_by_market.filter(round=round)
