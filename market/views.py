from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from random import randint
from .models import Market, Trader, Trade, RoundStat
from decimal import Decimal
from .forms import MarketForm, TraderForm, TradeForm
from .helpers import create_forced_trade, filter_trades, process_trade
from django.contrib.auth.decorators import login_required

@require_GET
def home(request):
    return render(request, 'market/home.html')

@login_required
@require_GET
def my_markets(request):
    markets = Market.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'market/my_markets.html', { 'markets': markets})

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
    return render(request, 'market/create.html', {'form': form})
            
def join(request):
    if request.method == 'POST':
        form = TraderForm(request.POST)
        if form.is_valid():
            market = Market.objects.get(market_id=form.cleaned_data['market_id'])

            new_trader = form.save(commit=False)
            new_trader.market = market
            new_trader.prod_cost = randint(market.min_cost, market.max_cost)
            new_trader.balance = Trader.initial_balance
            new_trader.save()
            
            request.session['trader_id'] = new_trader.pk
            request.session['username'] = form.cleaned_data['name']
            request.session['market_id'] = form.cleaned_data['market_id']

            # if player joins a game in round n>0, create forced trades for round 0,1,..,n-1 
            if market.round > 0:
                for round_num in range(market.round):
                    create_forced_trade(trader=new_trader, round_num=round_num, is_new_trader=True)
            return redirect(reverse('market:play'))

    elif request.method == 'GET':
        if 'market_id' in request.GET:
            form = TraderForm(
                initial={'market_id': request.GET['market_id']})
        else:
            form = TraderForm()
    return render(request, 'market/join.html', {'form':form})



def monitor(request, market_id):

    market = get_object_or_404(Market, market_id=market_id)
    traders = Trader.objects.filter(market=market)
    context = {
        'market': market,    
        'traders': traders,
        'rounds': range(market.round),
        'max_num_players': range(70),
        'show_stats_fields':['profit', 'balance_after', 'unit_price', 'unit_amount', 'demand', 'units_sold', 'was_forced'],
        'initial_balance':Trader.initial_balance
    }

    if request.method == "GET":
        return render(request, 'market/monitor.html', context)

    if request.method == "POST":

        real_trades = filter_trades(market=market, round=market.round)
        
        for trade in real_trades:
            assert(trade.was_forced is False), "Forced trade in 'real trades'"
        assert(len(real_trades) > 0), "No trades in market this round. Can't calculate avg. price."

        avg_price = sum([trade.unit_price for trade in real_trades]) / len(real_trades)
      
        for trade in real_trades: 
            process_trade(market, trade, avg_price)

        for trader in traders:
            traders_number_of_real_trades_this_round = filter_trades(market=market, round=market.round).filter(trader=trader).count()
            if traders_number_of_real_trades_this_round == 0:
                create_forced_trade(trader=trader, round_num=market.round, is_new_trader=False)       
        all_trades_this_round = filter_trades(market=market, round=market.round)        
        assert(len(all_trades_this_round) == len(traders)), f"Number of trades in this round does not equal num traders ."
        
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
        trades = Trade.objects.filter(trader=trader)

        context = {
            'market': market,
            'trader':trader,
            'form':form,
            'rounds':range(market.round),
            'initial_balance': Trader.initial_balance,
            'round_stats':RoundStat.objects.filter(market=market),
            'trades':trades,
            'wait':False,
            'show_last_round_data':False
        }

        if trades.filter(round=market.round).exists():
            context['wait'] = True
        
        elif market.round > 0:
            last_trade = trades.get(round=market.round -1)
            if type(last_trade.profit) is int:
                context['show_last_round_data'] = True

        return render(request, 'market/play.html', context)
           

@require_GET
def traders_this_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    traders = [trade.trader.name for trade in filter_trades(market=market, round=market.round)]
    data = {
        'traders':traders
    }
    return JsonResponse(data)


@require_GET
def trader_api(request, market_id):
    
    market = get_object_or_404(Market, market_id=market_id)

    traders = [
        {
            'name': trader.name,
            'prod_cost': trader.prod_cost,
            'balance': trader.balance,
            'ready': trader.is_ready()
        }
        for trader in Trader.objects.filter(market=market)
    ]
    
    num_ready_traders = filter_trades(market=market, round=market.round).count()

    data = {
        'traders': traders,
        'num_traders':len(traders),
        'num_ready_traders': num_ready_traders,

    }

    return JsonResponse(data)


@require_GET
def current_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    data = {
        'round':market.round
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
        avg_price = sum([trader.price for trader in round_stats]) / len(round_stats)
        data += str(avg_price) + ","
        avg_amount = sum([trader.amount for trader in round_stats]) / len(round_stats)
        data += str(avg_amount) + ","
        avg_profit = sum([trader.profit for trader in round_stats]) / len(round_stats)
        data += str(avg_profit) + ","
        for trader in market_traders:
            trader_stats = Stats.objects.get(round=r, market=market, trader=trader)
            data += str(trader_stats.balance) + ","
        data += "<br>"
    output = open(market.market_id + "_stats.csv", "w")
    output.write(data)
    output.close()
    return HttpResponse(data)
"""
