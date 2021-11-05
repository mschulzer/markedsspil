from math import floor
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from .models import Market, Trader, Trade, RoundStat, UnusedCosts
from .forms import MarketForm, MarketUpdateForm, TraderForm, TradeForm
from .helpers import create_forced_trade, process_trade, generate_balance_list, add_graph_context_for_monitor_page, generate_prod_cost_list
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .market_settings import SCENARIOS
from django.utils.translation import gettext as _


@login_required
def market_edit(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    if request.method == 'POST':
        form = MarketUpdateForm(request.POST, instance=market)
        if form.is_valid():
            form.save()
            messages.success(
                request, _(
                    "Du opdaterede markedet.")
            )

            return HttpResponseRedirect(reverse('market:monitor', args=(market.market_id,)))

    else:  # request.method = 'GET'
        form = MarketUpdateForm(instance=market)

    context = {
        "form": form,
        "market": market,
        "upper_limit_on_max_rounds": Market.UPPER_LIMIT_ON_MAX_ROUNDS
    }

    return render(request, "market/market_edit.html", context)


@require_GET
@login_required
def trader_table(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    return render(request, 'market/trader-table.html', {'market': market})


def add_context_for_join_form(context, request):
    """ Helper function used by view functions below """

    # If the client has already joined a market
    if 'trader_id' in request.session:

        # If trader is in database
        if Trader.objects.filter(id=request.session['trader_id']).exists():
            trader = Trader.objects.get(id=request.session['trader_id'])
            # If trader has been removed from market
            if trader.removed_from_market:
                request.session['removed_from_market'] = True

        # If trader has been deleted from database
        else:
            request.session['removed_from_market'] = True

        # We add this market to the context to notify the client
        market = get_object_or_404(
            Market, market_id=request.session['market_id'])
        context['market'] = market
    return context


@require_POST
def join_market(request):
    form = TraderForm(request.POST)

    if form.is_valid():
        market = Market.objects.get(
            market_id=form.cleaned_data['market_id'])

        new_trader = form.save(commit=False)
        new_trader.market = market
        new_trader.balance = market.initial_balance
        new_trader.round_joined = market.round
        new_trader.save()

        request.session['trader_id'] = new_trader.pk
        request.session['username'] = form.cleaned_data['name']
        request.session['market_id'] = form.cleaned_data['market_id']

        # If player joins a game in round n>0, create 'forced trades' for round 0,1,..,n-1
        if market.round > 0:
            for round_num in range(market.round):
                create_forced_trade(
                    trader=new_trader, round_num=round_num, is_new_trader=True)

        # After joining the market, the player is redirected to the play page
        return redirect(reverse('market:play', args=(market.market_id,)))

    context = add_context_for_join_form({'form': form}, request)
    return render(request, 'market/home.html', context)


@require_GET
def home(request):
    # If the client is following an invitation link to a market
    if 'market_id' in request.GET:
        # Fill out the market_id field in the form
        form = TraderForm(
            initial={'market_id': request.GET['market_id']})

    # If the client is just visiting the home-page base url
    else:
        # The form should be empty
        form = TraderForm()

    context = add_context_for_join_form({'form': form}, request)
    return render(request, 'market/home.html', context)


@login_required
def my_markets(request):

    if request.method == "POST":
        delete_market_id = request.POST['delete_market_id']
        market = get_object_or_404(Market, market_id=delete_market_id)
        market.deleted = True
        market.save()
        return HttpResponseRedirect(reverse('market:my_markets'))

    markets = Market.objects.filter(
        created_by=request.user, deleted=False).order_by('-created_at')

    return render(request, 'market/my_markets.html', {'markets': markets})


@login_required
def create_market(request):
    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            new_market = form.save(commit=False)
            new_market.created_by = request.user
            new_market.save()
            # if all traders are not to have equal production cost
            if new_market.min_cost < new_market.max_cost:
                # add min_cost og max_cost to the list of unused costs
                UnusedCosts(market=new_market, cost=new_market.min_cost).save()
                UnusedCosts(market=new_market, cost=new_market.max_cost).save()

            return redirect(reverse('market:monitor', args=(new_market.market_id,)))

    elif request.method == 'GET':
        form = MarketForm()

    context = {
        'form': form,
        'scenarios': SCENARIOS,
        'scenarios_json': json.dumps(SCENARIOS),
        'upper_limit_on_max_rounds': Market.UPPER_LIMIT_ON_MAX_ROUNDS
    }

    return render(request, 'market/create_market.html', context)


@require_POST
@login_required
def remove_trader_from_market(request):
    trader_id = request.POST['remove_trader_id']
    trader = get_object_or_404(Trader, id=trader_id)
    market = get_object_or_404(Market, market_id=trader.market.market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    trader.remove()
    return redirect(reverse('market:monitor', args=(trader.market.market_id,)))


@require_POST
@login_required
def toggle_monitor_auto_pilot_setting(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    market.monitor_auto_pilot = not market.monitor_auto_pilot
    market.save()
    return redirect(reverse('market:monitor', args=(market.market_id,)))


@require_POST
@login_required
def set_game_over(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    market.game_over = True
    market.save()

    return redirect(reverse('market:monitor', args=(market.market_id,)))


@require_POST
@login_required
def finish_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # If user is not the creator of the market, redirect to home page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    # Query the trade decisions made by the traders in the current round
    valid_trades = market.valid_trades_this_round()

    # Let's assert that there is at leat 1 valid trade. Otherwise we will get a zero division error,
    # when calculating the avg. price below.
    assert(len(valid_trades) >
           0), "No trades in market this round. Can't calculate avg. price."

    # Calculate the average price (will be used to calculate the demand for each traders good)
    avg_price = sum(
        [trade.unit_price for trade in valid_trades]) / len(valid_trades)

    # Process each of the valid trades
    for trade in valid_trades:
        process_trade(
            market, trade, avg_price)

    # Create 'forced trades' for all traders who did not make a trade in time
    for trader in market.all_traders():
        if not trader.is_ready():
            create_forced_trade(
                trader=trader, round_num=market.round, is_new_trader=False)

    # Let's assert that at this point, there is exactly one trade pr trader in the current round
    assert(len(market.all_trades_this_round()) == len(market.all_traders())
           ), f"Number of trades in this round does not equal num traders ."

    # Save data for charts
    round_stat = RoundStat.objects.create(
        market=market, round=market.round, avg_price=avg_price)

    active_or_bankrupt_traders = market.active_or_bankrupt_traders()

    round_stat.avg_balance_after = sum(
        [trader.balance for trader in active_or_bankrupt_traders])/len(active_or_bankrupt_traders)

    round_stat.avg_amount = sum(
        [trade.unit_amount for trade in valid_trades]) / len(valid_trades)

    round_stat.save()

    # Update trader production cost
    for trader in market.all_traders():
        new_cost = trader.prod_cost + market.cost_slope
        if new_cost > 0:
            trader.prod_cost = new_cost
            trader.save()

    # Update total production cost change
    market.accum_cost_change += market.cost_slope

    # Update market round
    market.round += 1

    # Check game over
    if market.check_game_over():
        market.game_over = True

    market.save()

    return redirect(reverse('market:monitor', args=(market.market_id,)))


@require_GET
def monitor(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # Only the user who created the market has permission to monitor page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    context = {
        'market': market,
        'rounds': range(1, market.round + 1),
        'show_stats_fields': ['balance_before', 'unit_price', 'profit', 'unit_amount', 'demand', 'units_sold'],
    }

    # Add context for graphs
    context = add_graph_context_for_monitor_page(context)

    return render(request, 'market/monitor.html', context)


@require_POST
def declare_bankruptcy(request, trader_id):
    trader = get_object_or_404(Trader, id=trader_id)

    # Only trader himself can declare himself bankrupt
    if not request.session['trader_id'] == int(trader_id):
        return HttpResponseRedirect(reverse('market:home'))

    trader.bankrupt = True
    trader.save()

    return redirect(reverse('market:play', args=(trader.market.market_id,)))


def play(request, market_id):
    # The market_id is not used in the function. But we need is as a parameter because we want it in the url on the player page.
    try:
        trader = Trader.objects.get(id=request.session['trader_id'])
    except:
        # if not trader in session return to home:
        return redirect(reverse('market:home'))
    else:
        if trader.removed_from_market:
            return HttpResponse(
                f"<br>You have been permanently removed from the market {market_id} by the market host. <br><br>You can rejoin the market with a new name.<br><br>Please contact the market host if you have any questions.")

        market = trader.market
        round_stats = RoundStat.objects.filter(market=market)
        trades = Trade.objects.filter(trader=trader)

        if request.method == 'POST':
            form = TradeForm(data=request.POST)
            if form.is_valid():
                new_trade = form.save(commit=False)
                new_trade.trader = trader
                new_trade.round = market.round
                new_trade.balance_before = trader.balance
                new_trade.prod_cost = trader.prod_cost
                new_trade.save()

                auto_play = form.cleaned_data['auto_play']
                if auto_play:
                    trader.auto_play = True
                    trader.save()
                return redirect(reverse('market:play', args=(market.market_id,)))

        elif request.method == 'GET':

            if market.round > 0 and round_stats.last() is not None:
                market_average = round_stats.last().avg_price
                form = TradeForm(trader, market_average)
            else:
                form = TradeForm(trader)

        # Set x-axis for graphs
        if market.endless:
            round_labels = list(range(1, market.round + 2))
        else:
            round_labels = list(range(1, market.max_rounds + 1))

        context = {
            'market': market,
            'trader': trader,
            'form': form,
            'round_stats': round_stats,
            'trades': trades,
            'max_amount': floor(trader.balance/trader.prod_cost),
            'max_price': 4 * market.max_cost,

            # Labels for x-axis for graphs
            'round_labels_json': json.dumps(round_labels),

            # data for units graph
            'data_demand_json': json.dumps([trade.demand for trade in trades]),
            'data_sold_json': json.dumps([trade.units_sold for trade in trades]),
            'data_produced_json': json.dumps([trade.unit_amount if (trade.unit_amount != None) else None for trade in trades]),

            # data for price graph
            'data_price_json': json.dumps([float(trade.unit_price) if (trade.unit_price != None) else None for trade in trades]),
            'data_prod_cost_json': json.dumps(generate_prod_cost_list(market, trades, trader)),
            'data_market_avg_price_json': json.dumps([float(round_stat.avg_price) for round_stat in round_stats]),

            # add data for balance graph
            'trader_balance_json': json.dumps(
                generate_balance_list(trader)),
            'avg_balance_json': json.dumps([float(market.initial_balance)] +
                                           [float(round_stat.avg_balance_after) for round_stat in round_stats])
        }

        context['wait'] = trader.should_be_waiting()

        return render(request, 'market/play/play.html', context)


@require_GET
def current_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    return JsonResponse(
        {
            'round': market.round,
            'num_active_traders': market.num_active_traders(),
            'num_ready_traders': market.num_ready_traders(),
            'game_over': market.game_over
        }
    )


# def download(request, market_id):
#     # not properly tested yet
#     # known issues:
#     # if trader_stats does not exist for all traders in all rounds script will crash.
#     market = get_object_or_404(Market, market_id=market_id)
#     market_traders = Trader.objects.filter(market=market)
#     total_rounds = market.round
#     data = "Round,Average price,Average amount,Average profit,"
#     for trader in market_traders:
#         data += trader.name + " balance,"
#     data += "<br>"
#     for r in range(total_rounds):
#         data += str(r) + ","
#         round_stats = Stats.objects.filter(round=r, market=market)
#         avg_price = sum(
#             [trader.price for trader in round_stats]) / len(round_stats)
#         data += str(avg_price) + ","
#         avg_amount = sum(
#             [trader.amount for trader in round_stats]) / len(round_stats)
#         data += str(avg_amount) + ","
#         avg_profit = sum(
#             [trader.profit for trader in round_stats]) / len(round_stats)
#         data += str(avg_profit) + ","
#         for trader in market_traders:
#             trader_stats = Stats.objects.get(
#                 round=r, market=market, trader=trader)
#             data += str(trader_stats.balance) + ","
#         data += "<br>"
#     output = open(market.market_id + "_stats.csv", "w")
#     output.write(data)
#     output.close()
#     return HttpResponse(data)
