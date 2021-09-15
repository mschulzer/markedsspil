from django.utils.safestring import mark_safe
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from .models import Market, Trader, Trade, RoundStat, UnusedCosts, UsedCosts
from .forms import MarketForm, MarketUpdateForm, TraderForm, TradeForm
from .helpers import create_forced_trade, filter_trades, process_trade, generate_balance_list, generate_cost_list, add_graph_context_for_monitor_page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .market_settings import SCENARIOS
from django.utils.translation import gettext as _


@login_required
def market_edit(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # Only the user who created the market has access to this edit page
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    if request.method == 'POST':
        form = MarketUpdateForm(request.POST, instance=market)
        if form.is_valid():
            form.save()
            messages.success(
                request, _(
                    "You updated the market.")
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
def trader_table(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    traders = Trader.objects.filter(market=market).order_by('-balance')
    num_ready_traders = filter_trades(
        market=market, round=market.round).count()
    context = {
        'market': market,
        'traders': traders,
        'num_ready_traders': num_ready_traders,
    }
    return render(request, 'market/trader-table.html', context)


@require_GET
def small_trader_table(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    traders = Trader.objects.filter(market=market).order_by('-balance')
    context = {
        'traders': traders,
        'market': market
    }
    return render(request, 'market/small-trader-table.html', context)


@require_GET
def home(request):
    context = {}
    if 'market_id' in request.session:
        market = Market.objects.get(
            market_id=request.session['market_id'])
        context['market'] = market
    return render(request, 'market/home.html', context)


@login_required
@require_GET
def my_markets(request):
    markets = Market.objects.filter(
        created_by=request.user).order_by('-created_at')
    return render(request, 'market/my_markets.html', {'markets': markets})


@login_required
def create(request):

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

    return render(request, 'market/create.html', context)


def join(request):

    if request.method == 'POST':
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

            # if player joins a game in round n>0, create forced trades for round 0,1,..,n-1
            if market.round > 0:
                for round_num in range(market.round):
                    create_forced_trade(
                        trader=new_trader, round_num=round_num, is_new_trader=True)

            return redirect(reverse('market:play', args=(market.market_id,)))

    elif request.method == 'GET':
        if 'market_id' in request.GET:
            form = TraderForm(
                initial={'market_id': request.GET['market_id']})
        else:
            form = TraderForm()

        if 'market_id' in request.session:
            market = Market.objects.get(
                market_id=request.session['market_id'])

            messages.warning(request, mark_safe(
                f"Hi {request.session['username']}! You've already joined the {market.product_name_singular}-markedet {market.market_id}. If you submit the form below, you will permanenly lose access to this market. Do you want to return to your current market?<a href='/{market.market_id}/play'> Return to my market </a>"))
            # f"Hej {request.session['username']}! Du deltager allerede i {market.product_name_singular}-markedet {market.market_id}. Hvis du indsender formularen nedenfor, mister du permanent adgang til dette marked. Vil du tilbage til dit marked?<a href='/{market.market_id}/play'> Tilbage til mit marked </a>"))

    return render(request, 'market/join.html', {'form': form})


def monitor(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # Unless game_over, only the user who created the market has permission to monitor page
    if not request.user == market.created_by:
        if not market.game_over():
            return HttpResponseRedirect(reverse('market:home'))

    traders = Trader.objects.filter(market=market).order_by('-balance')

    context = {
        'market': market,
        'traders': traders,
        'num_ready_traders': filter_trades(market=market, round=market.round).count(),
        'rounds': range(1, market.round + 1),
        'show_stats_fields': ['balance_before', 'unit_price', 'profit', 'unit_amount', 'demand', 'units_sold'],
        'initial_balance': market.initial_balance

    }

    if request.method == "GET":
        if market.game_over():
            messages.success(request, mark_safe(
                "The game has ended after {0} rounds!".format(market.round)
            ))

        # add context for graphs
        context = add_graph_context_for_monitor_page(context, market, traders)

        return render(request, 'market/monitor.html', context)

    if request.method == "POST":
        # The host has pressed the 'next round' button
        real_trades = filter_trades(market=market, round=market.round)

        for trade in real_trades:
            assert(trade.was_forced is False), "Forced trade in 'real trades'"
        assert(len(real_trades) >
               0), "No trades in market this round. Can't calculate avg. price."

        avg_price = sum(
            [trade.unit_price for trade in real_trades]) / len(real_trades)

        for trade in real_trades:
            process_trade(
                market, trade, avg_price)

        for trader in traders:
            traders_number_of_real_trades_this_round = filter_trades(
                market=market, round=market.round).filter(trader=trader).count()
            if traders_number_of_real_trades_this_round == 0:
                create_forced_trade(
                    trader=trader, round_num=market.round, is_new_trader=False)

        all_trades_this_round = filter_trades(
            market=market, round=market.round)
        assert(len(all_trades_this_round) == len(traders)
               ), f"Number of trades in this round does not equal num traders ."

        # data for charts
        round_stat = RoundStat.objects.create(
            market=market, round=market.round, avg_price=avg_price)

        round_stat.avg_balance_after = sum(
            [trader.balance for trader in traders])/len(traders)

        round_stat.avg_amount = sum(
            [trade.unit_amount for trade in real_trades]) / len(real_trades)

        round_stat.save()

        # Update market round
        market.round += 1
        market.save()

        return redirect(reverse('market:monitor', args=(market.market_id,)))


def play(request, market_id):

    try:
        trader = Trader.objects.get(id=request.session['trader_id'])
    except:
        return redirect(reverse('market:join'))
    else:
        market = trader.market

        if request.method == 'POST':
            form = TradeForm(data=request.POST)
            if form.is_valid():
                new_trade = form.save(commit=False)
                new_trade.trader = trader
                new_trade.round = market.round
                new_trade.balance_before = trader.balance
                new_trade.save()
                return redirect(reverse('market:play', args=(market.market_id,)))
        else:
            form = TradeForm(trader)

        round_stats = RoundStat.objects.filter(market=market)
        trades = Trade.objects.filter(trader=trader)

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
            'wait': False,
            'traders': Trader.objects.filter(market=market).order_by('-balance'),

            # Labels for x-axis for graphs
            'round_labels_json': json.dumps(round_labels),

            # data for units graph
            'data_demand_json': json.dumps([trade.demand for trade in trades]),
            'data_sold_json': json.dumps([trade.units_sold for trade in trades]),
            'data_produced_json': json.dumps([trade.unit_amount for trade in trades]),

            # data for price graph
            'data_price_json': json.dumps([float(trade.unit_price) if trade.unit_price else None for trade in trades]),
            'data_prod_cost_json': json.dumps(generate_cost_list(trader)),
            'data_market_avg_price_json': json.dumps([float(round_stat.avg_price) for round_stat in round_stats]),

            # data for balance graph
            'trader_balance_json': json.dumps(generate_balance_list(trader)),
            'avg_balance_json': json.dumps([float(market.initial_balance)] + [float(round_stat.avg_balance_after) for round_stat in round_stats])
        }

        if trades.filter(round=market.round).exists():
            context['wait'] = True
            messages.success(
                request,
                _("You made a trade!")
            )

        else:
            # player should not be waiting
            if market.game_over():
                messages.info(request,  mark_safe(
                    # f"The game has ended after {market.max_rounds} rounds!<br><a href='/{market.market_id}/monitor' target='_blank'>Monitor market</a>."))
                    f"The game has ended after {market.max_rounds} rounds."))

            else:  # game is not over
                if market.round == trader.round_joined:
                    # a verbose & enthusiastic message welcoming new traders
                    if market.endless:
                        messages.success(
                            request, _("Hi {0}! You are now ready for round {1} on the {2} market {3}.").format(trader.name, market.round + 1, market.product_name_singular, market.market_id))
                    else:
                        messages.success(
                            request, _("Hi {0}! You are now ready for round {1} out of {2} on the {3} market {4}.").format(trader.name, market.round + 1, market.max_rounds, market.product_name_singular, market.market_id))
                else:
                    # a less verbose and less enthusiastic message for other traders
                    if market.endless:
                        messages.success(
                            request, _("You are now ready for round {0}.").format(market.round + 1))
                    else:
                        if not messages.get_messages(request):
                            messages.success(
                                request, _("You are now ready for round {0} out of {1}.").format(market.round + 1, market.max_rounds))

        return render(request, 'market/play.html', context)


@require_GET
def current_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    data = {
        'round': market.round,
    }
    return JsonResponse(data)


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
