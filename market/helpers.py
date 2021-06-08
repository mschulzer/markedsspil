"""
Helper functions used by the views
"""

from .models import Market, Trader, Trade
from decimal import Decimal
from math import floor


def process_trade(market, trade, avg_price):
    """
    Calculates key values for a single trade and updates trade and trader accordingly.
    Used by monitor-view on post-requests, when host finishes a round
    """

    alpha, beta, theta = float(market.alpha), float(market.beta), float(market.theta)  

    # calculate values
    expenses = trade.trader.prod_cost * trade.unit_amount  
    demand = alpha - beta * trade.unit_price + theta * \
        avg_price   

    units_sold = floor(max(0, min(demand, trade.unit_amount))) 
    income = trade.unit_price * units_sold  
    trade_profit = income - expenses   

    # assert datatypes and values, and update trade and trader objects
    assert(type(units_sold) is int)
    assert(units_sold >= 0)
    trade.units_sold = units_sold

    assert(type(trade_profit) is int)
    trade.profit = round(trade_profit)
    trader = trade.trader
    trader.balance += trade_profit
    trade.balance_after = trader.balance

    assert(trader.balance == trade.balance_after)

    # save to database
    trader.save()
    trade.save()


    return demand, expenses, units_sold, income, trade_profit



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

def filter_trades(market, round="all_rounds"):
    trades_by_market = Trade.objects.filter(trader__in=Trader.objects.filter(market=market))
    if round == "all_rounds":
        return trades_by_market
    else:
        assert(type(round) == int)
        return trades_by_market.filter(round=round)
