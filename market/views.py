from django.utils.safestring import mark_safe
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from .models import Market, Trader, Trade, RoundStat
from .forms import MarketForm, MarketUpdateForm, TraderForm, TradeForm
from .helpers import create_forced_trade, filter_trades, process_trade
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .market_settings import SCENARIOS
from django.utils.translation import gettext as _
from decimal import Decimal
from django.utils.safestring import mark_safe


@login_required
def market_edit(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # only the user how created the market has permission to edit it
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    if request.method == 'POST':
        form = MarketUpdateForm(request.POST, instance=market)
        if form.is_valid():
            form.save()
            messages.success(
                request, _("You successfully updated the market. Changes will take effect from this round forward."))

            return HttpResponseRedirect(reverse('market:monitor', args=(market.market_id,)))

    else:  # request.method = 'GET'
        form = MarketUpdateForm(instance=market)

    context = {"form": form, "market": market}

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
    }
    return render(request, 'market/small-trader-table.html', context)


@require_GET
def home(request):
    return render(request, 'market/home.html')


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
            return redirect(reverse('market:monitor', args=(new_market.market_id,)))

    elif request.method == 'GET':
        form = MarketForm()

    context = {'form': form, 'scenarios': SCENARIOS,
               'scenarios_json': json.dumps(SCENARIOS)}

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

            return redirect(reverse('market:play'))

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
                f"Hi {request.session['username']}! You've already joined the {market.product_name_singular}-markedet {market.market_id}. If you submit the form below, you will permanenly lose access to this market. Do you want to return to your current market?<a href='/play'> Return to market </a>"))
            # f"Hej {request.session['username']}! Du deltager allerede i {market.product_name_singular}-markedet {market.market_id}. Hvis du indsender formularen nedenfor, mister du permanent adgang til dette marked. Vil du tilbage til dit marked?<a href='/play'> Tilbage til mit marked </a>"))

    return render(request, 'market/join.html', {'form': form})


@login_required
def monitor(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)

    # only the user how created the market has permission to monitor it
    if not request.user == market.created_by:
        return HttpResponseRedirect(reverse('market:home'))

    traders = Trader.objects.filter(market=market).order_by('-balance')

    context = {
        'market': market,
        'traders': traders,
        'num_ready_traders': filter_trades(market=market, round=market.round).count(),
        'rounds': range(market.round),
        'show_stats_fields': ['profit', 'balance_after', 'unit_price', 'unit_amount', 'demand', 'units_sold', 'was_forced'],
        'initial_balance': market.initial_balance
    }

    if request.method == "GET":
        return render(request, 'market/monitor.html', context)

    if request.method == "POST":

        real_trades = filter_trades(market=market, round=market.round)

        for trade in real_trades:
            assert(trade.was_forced is False), "Forced trade in 'real trades'"
        assert(len(real_trades) >
               0), "No trades in market this round. Can't calculate avg. price."

        avg_price = sum(
            [trade.unit_price for trade in real_trades]) / len(real_trades)

        for trade in real_trades:
            process_trade(market, trade, avg_price)

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

        RoundStat.objects.create(
            market=market, round=market.round, avg_price=avg_price)

        market.round += 1
        market.save()

        return redirect(reverse('market:monitor', args=(market.market_id,)))


def play(request):

    try:
        trader = Trader.objects.get(id=request.session['trader_id'])
    except:
        return redirect(reverse('market:join'))
    else:
        market = trader.market

        if request.method == 'POST':
            form = TradeForm(data=request.POST)
            assert(form.is_valid), 'TradeForm invalid - This should not be possible'
            if form.is_valid():
                new_trade = form.save(commit=False)
                new_trade.trader = trader
                new_trade.round = market.round
                new_trade.save()
            return redirect(reverse('market:play'))

        # Get requests only :

        form = TradeForm(trader)
        round_stats = RoundStat.objects.filter(market=market)
        trades = Trade.objects.filter(trader=trader)

        context = {
            'market': market,
            'trader': trader,
            'form': form,
            'round_stats': round_stats,
            'trades': trades,
            'wait': False,
            'traders': Trader.objects.filter(market=market).order_by('-balance'),


            # labels for x-axis on charts
            'rounds_json': json.dumps(list(range(1, market.round + 2))),

            # context for units graph
            'data_demand_json': json.dumps([trade.demand for trade in trades]),
            'data_sold_json': json.dumps([trade.units_sold for trade in trades]),
            'data_produced_json': json.dumps([trade.unit_amount for trade in trades]),

            # context for price graph
            'data_price_json': json.dumps([float(trade.unit_price) if trade.unit_price else None for trade in trades]),
            'data_prod_cost_json': json.dumps([float(trader.prod_cost) for _ in trades]),
            'data_market_avg_price_json': json.dumps([float(round_stat.avg_price) for round_stat in round_stats]),

            # context for balance graph
            'data_balance_json': json.dumps([float(market.initial_balance) if trader.round_joined == 0 else None] + [float(trade.balance_after) if trade.balance_after else None for trade in trades]),
        }

        if trades.filter(round=market.round).exists():
            context['wait'] = True
            messages.success(
                request,
                _("You made a trade, {0}!").format(trader.name))

        else:  # player should not be waiting

            if market.game_over():
                messages.info(request,  mark_safe(
                    f"You made your last trade! The game has ended after {market.max_rounds} rounds. <a href='/{market.market_id}/game_over' target='_blank'> Åbn markedsoversigt</a>."))

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
                            request, _("Hi {0}. You are now ready for round {1}.").format(request.session["username"], market.round + 1))
                    else:
                        if not messages.get_messages(request):
                            messages.success(
                                request, _("Hi {0}. You are now ready for round {1} out of {2}.").format(request.session["username"], market.round + 1, market.max_rounds))

        return render(request, 'market/play.html', context)


@ require_GET
def current_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    data = {
        'round': market.round,
    }
    return JsonResponse(data)


"""
def download(request, market_id):
    # not properly tested yet
    # known issues:
    # if trader_stats does not exist for all traders in all rounds script will crash.
    market = get_object_or_404(Market, market_id=market_id)
    market_traders = Trader.objects.filter(market=market)
    total_rounds = market.round
    data = "Round,Average price,Average amount,Average profit,"
    for trader in market_traders:
        data += trader.name + " balance,"
    data += "<br>"
    for r in range(total_rounds):
        data += str(r) + ","
        round_stats = Stats.objects.filter(round=r, market=market)
        avg_price = sum(
            [trader.price for trader in round_stats]) / len(round_stats)
        data += str(avg_price) + ","
        avg_amount = sum(
            [trader.amount for trader in round_stats]) / len(round_stats)
        data += str(avg_amount) + ","
        avg_profit = sum(
            [trader.profit for trader in round_stats]) / len(round_stats)
        data += str(avg_profit) + ","
        for trader in market_traders:
            trader_stats = Stats.objects.get(
                round=r, market=market, trader=trader)
            data += str(trader_stats.balance) + ","
        data += "<br>"
    output = open(market.market_id + "_stats.csv", "w")
    output.write(data)
    output.close()
    return HttpResponse(data)
"""
