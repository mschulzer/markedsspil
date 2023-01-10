"""
Helper functions used by the views
"""

from .models import Trader, Trade, RoundStat
import json


def process_trade(market, trade, avg_price):
    """
    Calculates key values for a single trade and updates trade and trader accordingly.
    Used by monitor-view on post-requests, when host finishes a round
    """
    alpha, theta, gamma = market.alpha, market.theta, market.gamma

    # calculate values
    expenses = trade.trader.prod_cost * trade.unit_amount
    raw_demand = alpha - (gamma + theta) * trade.unit_price + theta * avg_price
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
        prod_cost = None
    else:
        # situation 2
        balance_after = trader.balance
        balance_before = trader.balance
        prod_cost = trader.prod_cost

    forced_trade = Trade.objects.create(
        round=round_num,
        trader=trader,
        unit_price=None,
        unit_amount=None,
        demand=None,
        balance_after=balance_after,
        balance_before=balance_before,
        profit=None,
        was_forced=True,
        prod_cost=prod_cost
    )
    return forced_trade


def generate_prod_cost_list(market, trades, trader):

    prod_costs = [float(trade.prod_cost) if (
        trade.prod_cost != None) else None for trade in trades]

    if not trader.should_be_waiting():
        prod_costs += [float(trader.prod_cost)]

    return prod_costs


def generate_balance_list(trader):
    """
    Generates a list of floats consisting of the balances of a single trader.
    The i'th entry of the list is the balance before/during each round, not the
    balance after the round.  

    For a trader, who joins the game in the first round, the resulting list
    should loook something like this
    [Initial_balance, 405, 405, 410, 49, ...] 

    For a trader who joined the game in "round 3" (market.round=2), 
    the list should look something like this: 
    [None, None, Initial_balance, 405, 405, 410, 49, ...] 

    The length of the list should equal market.round + 1, as there should be one
    balance for each round, including the current round. 
    """
    trades = Trade.objects.filter(
        trader=trader, round__lte=trader.market.round - 1)
    initial_balance = float(trader.market.initial_balance)

    balance_list = [initial_balance] + \
        [float(trade.balance_after)
         if (trade.balance_after != None) else None for trade in trades]

    if trader.round_joined > 0:
        balance_list[0] = None
        balance_list[trader.round_joined] = initial_balance

    return balance_list


def add_graph_context_for_monitor_page(context):
    """ 
    This function produces all the data for the graphs on the monitor pages
    """
    market = context['market']

    # Labels for x-axes of graphs
    if market.endless:
        round_labels = list(range(1, market.round + 2))
    else:
        round_labels = list(range(1, market.max_rounds + 1))
    context['round_labels_json'] = json.dumps(round_labels)

    # Data for balance and amount graphs
    # If the app gets slow, we should refactor and optimize

    color_for_averages = 'blue'

    def generate_price_list(trader):
        # On the monitor page price graph, we only want to show data for previous rounds.
        trades = Trade.objects.filter(
            trader=trader, round__lte=market.round - 1)
        return [float(trade.unit_price) if (trade.unit_price != None) else None for trade in trades]

    def generate_amount_list(trader):
        # On the monitor page amount graph, we only want to show data for previous rounds.
        trades = Trade.objects.filter(
            trader=trader, round__lte=market.round - 1)

        return [float(trade.unit_amount) if (trade.unit_amount != None) else None for trade in trades]

    def trader_color(i):
        """
        Pseudo random colors to be used in multi-player plots. 
        Perhaps we should select the first x colors from a list of colors that look nice together... 
        """
        i += 300  # the first few colors look okay with this choice
        red = (100 + i*100) % 255
        green = (50 + int((i/3)*100)) % 255
        blue = (0 + int((i/2)*100)) % 255
        return f"rgb({red},{green},{blue}, 0.3)"

    # We want graphs to show data for all (including possibly removed) traders
    all_traders = market.all_traders()

    balanceDataSet = [{
        'label': trader.name,
        'backgroundColor': trader_color(i),
        'borderColor': trader_color(i),
        'data': generate_balance_list(trader)
    }
        for i, trader in enumerate(all_traders)
    ]

    priceDataSet = [{
        'label': trader.name,
        'backgroundColor': trader_color(i),
        'borderColor': trader_color(i),
        'data': generate_price_list(trader)
    }
        for i, trader in enumerate(all_traders)
    ]

    amountDataSet = [{
        'label': trader.name,
        'backgroundColor': trader_color(i),
        'borderColor': trader_color(i),
        'data': generate_amount_list(trader)
    }
        for i, trader in enumerate(all_traders)
    ]

    active_or_bankrupt_traders = market.active_or_bankrupt_traders()

    # If at least one trader is participating in the market (bankrupt or non-bankrupt):
    if active_or_bankrupt_traders:
        # We add average data to graph datasets

        round_stats = RoundStat.objects.filter(market=market)

        # Average balances
        avg_balances = [float(market.initial_balance)] + [float(round_stat.avg_balance_after)
                                                          for round_stat in round_stats]
        # the average balance in the current round might change during the round (due to new traders joining the market),
        # so we update this value on each page reload:
        avg_balance_this_round_so_far = sum(
            [trader.balance for trader in active_or_bankrupt_traders])/len(active_or_bankrupt_traders)
        avg_balances[-1] = float(avg_balance_this_round_so_far)

        balanceDataSet.append({
            'label': 'Average',
            'backgroundColor': color_for_averages,
            'borderColor': color_for_averages,
            'data': avg_balances,
            'borderWidth': 2
        })

        # Average prices
        avg_prices = [float(round_stat.avg_price)
                      for round_stat in round_stats]

        priceDataSet.append({
            'label': 'Average',
            'backgroundColor': color_for_averages,
            'borderColor': color_for_averages,
            'data': avg_prices,
            'borderWidth': 2
        })

        # Average units produced
        avg_amounts = [float(round_stat.avg_amount)
                       for round_stat in round_stats]

        amountDataSet.append({
            'label': 'Avg. amount',
            'backgroundColor': color_for_averages,
            'borderColor': color_for_averages,
            'data': avg_amounts,
            'borderWidth': 2
        })

    context['balanceDataSet'] = json.dumps(balanceDataSet)
    context['priceDataSet'] = json.dumps(priceDataSet)
    context['amountDataSet'] = json.dumps(amountDataSet)
    return context
