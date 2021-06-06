from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from random import randint
from .models import Market, Trader, Trade, RoundStat
from decimal import Decimal
from .forms import MarketForm, TraderForm, TradeForm
from .helpers import create_forced_trade, filter_trades

@require_GET
def home(request):
    return render(request, 'market/home.html')

def create(request):
    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            new_market = form.save()
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
        'show_stats_fields':['profit', 'balance_after', 'unit_price', 'unit_amount', 'was_forced'],
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

        alpha, beta, theta = market.alpha, market.beta, market.theta
        for trade in real_trades: 
            # calculate values 
            demand = alpha - beta * Decimal(trade.unit_price) + theta * Decimal(avg_price)
            expenses = trade.trader.prod_cost * trade.unit_amount
            units_sold = min(demand, trade.unit_amount)
            income = trade.unit_price * units_sold
            trade_profit = income - expenses
            # store values
            trade.units_sold = units_sold
            trade.profit = trade_profit
            trader = trade.trader
            trader.balance += trade_profit 
            trade.balance_after = trader.balance
            trader.save()
            trade.save()
      
        for trader in traders:
            traders_number_of_real_trades_this_round = filter_trades(market=market, round=market.round).filter(trader=trader).count()
            if traders_number_of_real_trades_this_round == 0:
                create_forced_trade(trader=trader, round_num=market.round, is_new_trader=False)
                
        all_trades_this_round = filter_trades(market=market, round=market.round)        
        assert(len(all_trades_this_round) == len(traders)), f"Number of trades in this round does not equal num traders ."
        
        market.round += 1
        market.save()

        RoundStat.objects.create(
            market=market, round=market.round, avg_price=avg_price)

        return redirect(reverse('market:monitor', args=(market.market_id,)))
  

def play(request):

    try:
        trader = Trader.objects.get(id=request.session['trader_id'])
    except:
        return redirect(reverse('market:join'))
    else:
        market = trader.market
        context = {'market': trader.market, 'trader': trader}
        
        last_round_data_available = False
        if market.round > 0:
            traders_last_trade = Trade.objects.get(trader=trader, round=market.round - 1)
            if not traders_last_trade.was_forced:
                last_round_data_available = True

        if request.method == 'POST':
            form = TradeForm(data=request.POST)
            if form.is_valid():
                new_trade = form.save(commit=False)
                new_trade.trader = trader
                new_trade.round = market.round
                new_trade.save()
                return redirect(reverse('market:play'))
            
        elif request.method == 'GET':
            context = {'market': trader.market, 'trader': trader}
            has_traded_this_round = Trade.objects.filter(trader=trader, round=market.round).exists()
            if has_traded_this_round:
                return render(request, 'market/wait.html', context )
            
            if not last_round_data_available:
                form = TradeForm(trader)
            else:            
                last_price = traders_last_trade.unit_price
                last_amount = traders_last_trade.unit_amount
                form = TradeForm(trader,
                    initial={'unit_price': last_price, 'unit_amount': last_amount})

        context['last_round_data_available'] = last_round_data_available         
        context['form'] = form
        context['rounds'] = range(market.round)
        context['initial_balance'] = Trader.initial_balance
        context['round_stats'] = RoundStat.objects.filter(market=market)
        trades = Trade.objects.filter(trader=trader)
        context['trades'] = trades
        if trader.balance >= Trader.initial_balance:
            context['total_gain_color'] = "blue"
        else:
            context['total_gain_color'] = "red"

        if last_round_data_available:
            if trades.last().profit >= 0:
                context['last_round_gain_color'] = "blue"
            else:
                context['last_round_gain_color'] = "red"

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
