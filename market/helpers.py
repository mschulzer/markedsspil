"""
Helper functions used by the views
"""

from .models import Trader, Trade


def process_trade(market, trade, avg_price):
    """
    Calculates key values for a single trade and updates trade and trader accordingly.
    Used by monitor-view on post-requests, when host finishes a round
    """
    alpha, beta, theta = market.alpha, market.beta, market.theta

    # calculate values
    expenses = trade.trader.prod_cost * trade.unit_amount
    raw_demand = alpha - beta * trade.unit_price + theta * avg_price
    demand = max(0, round(raw_demand))
    units_sold = min(demand, trade.unit_amount)
    income = trade.unit_price * units_sold
    trade_profit = income - expenses

    assert(units_sold >= 0)

    # update trade and trader objects
    trade.demand = demand
    trade.units_sold = units_sold
    trade.profit = trade_profit
    trader = trade.trader
    trader.balance += trade_profit
    trade.balance_after = trader.balance

    # save to database
    trader.save()
    trade.save()

    return expenses, raw_demand, demand, units_sold, income, trade_profit


def create_forced_trade(trader, round_num, is_new_trader):
    """
    Used in two different situations:
    1) To create a "null trade" for round 0,1,2,..., n-1 for a trader who has entered the game in a round n
    2) To create a "null trade" for the current round for a trader who joined in a previos round but did not trade in current round

    """
    if is_new_trader:
        # situation 1
        balance_before = None
        balance_after = None
    else:
        # situation 2
        balance_after = trader.balance
        balance_before = trader.balance

    forced_trade = Trade.objects.create(
        round=round_num,
        trader=trader,
        unit_price=None,
        unit_amount=None,
        demand=None,
        balance_after=balance_after,
        balance_before=balance_before,
        profit=None,
        was_forced=True
    )
    return forced_trade


def filter_trades(market, round="all_rounds"):
    trades_by_market = Trade.objects.filter(
        trader__in=Trader.objects.filter(market=market))
    if round == "all_rounds":
        return trades_by_market
    else:
        assert(type(round) == int)
        return trades_by_market.filter(round=round)


def generate_balance_list(trader):
    """
    Generates a list of floats consisting of the balance history of a single trader.
    The i'th entry of the list is the balance before/during each round, not the
    balance after the round.  

    For a trader, who joins the game in the first round, the resulting list
    should loook something like this
    [Initial_balance, 405, 405, 410, 49, ...] 

    For a trader who joined the game in "round 3" (market.round=2), 
    the list should look something like this: 
    [None, None, Initial_balance, 405, 405, 410, 49, ...] 
    """
    trades = Trade.objects.filter(trader=trader)
    initial_balance = float(trader.market.initial_balance)

    balance_list = [initial_balance] + \
        [float(trade.balance_after)
         if trade.balance_after else None for trade in trades]

    if trader.round_joined > 0:
        balance_list[0] = None
        balance_list[trader.round_joined] = initial_balance

    return balance_list


def generate_cost_list(trader):
    """
    Generates a list of floats consisting of the prod_cost of a single trader.
    The i'th entry of the list is the prod_cost in the i'th round. It should be either None, 
    if the trader has not joined yet, or equal to the trader's fixed prod. cost. 

    For a trader, who joins the game in the first round, the resulting list
    should loook something like this
    [8, 8, 8,...,8] 

    For a trader who joined the game in "round 3" (market.round=2), 
    the list should look something like this: 
    [None, None, 8, 8, 8, ...,8] 
    """
    prod_cost = float(trader.prod_cost)

    prod_cost_list = [prod_cost for _ in range(trader.market.round + 1)]

    if trader.round_joined > 0:
        for i in range(trader.round_joined):
            prod_cost_list[i] = None
    return prod_cost_list
