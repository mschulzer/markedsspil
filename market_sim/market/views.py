from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from random import randint

from .models import Market, Trader, Trade, Stats
from decimal import Decimal
from .forms import MarketForm, TraderForm

def join(request):
    if request.method == 'POST':
        form = TraderForm(request.POST)
        if form.is_valid():
            market = Market.objects.get(market_id=form.cleaned_data['market_id'])
            new_trader = market.trader_set.create(name=form.cleaned_data['username'])
            new_trader.money = 5000
            new_trader.prod_cost = randint(market.min_cost, market.max_cost)
            new_trader.save()
            request.session['trader_id'] = new_trader.pk
            return HttpResponseRedirect(reverse('market:play', args=(market.market_id,)))
    else:
        if 'market_id' in request.session:
            form = TraderForm(initial={'market_id': request.session['market_id']})
        else:
            form = TraderForm()
    return render(request, 'market/join.html', {'form':form})

def create(request):
    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            new_market = form.save()
            return HttpResponseRedirect(reverse('market:monitor', args=(new_market.market_id,)))
    else:
        form = MarketForm()

    return render(request, 'market/create.html', {'form': form})

def monitor(request, market_id):
    try:
        market = get_object_or_404(Market, market_id=market_id)
        traders = Market.objects.filter(market_id=market_id)
    except:
        print("Failed retrieving market")
        return HttpResponseRedirect('/market/creator.html')
    else:
        return render(request, 'market/monitor.html', {'market':market,'traders':traders})

def play(request, market_id):
    try:
        market = Market.objects.get(market_id=market_id)
    except DoesNotExist:
        return HttpResponseRedirect('market')
    else:
        try:
            trader = Trader.objects.get(pk=request.session['trader_id'])
        except:
            request.session['market_id'] = market.market_id
            return HttpResponseRedirect('/market')
        else:
            unit_cost = trader.prod_cost
            print(request.session['trader_id'])
            print(trader)
            return render(request, 'market/play.html', {'market':market,
                                                        'trader':trader,
                                                        'unit_cost':unit_cost})

def sell(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    trader = get_object_or_404(Trader, pk=request.session['trader_id'])
    price = request.POST['price']
    amount = request.POST['amount']
    new_trade = Trade(market=market,
                      trader=trader,
                      unit_price=price,
                      unit_amount=amount,
                      round=market.round)
    print(new_trade)
    new_trade.save()
    return HttpResponseRedirect(reverse('market:wait', args=(market_id,)))

def wait(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    return render(request, 'market/wait.html', {'market':market})

def traders_in_market(request, market_id):
    print(market_id)
    market = Market.objects.get(market_id=market_id)
    traders = [x.name for x in Trader.objects.filter(market=market)]
    data = {
        'traders':traders
    }
    return JsonResponse(data)

def traders_this_round(request, market_id):
    round = request.GET['round_num']
    traders = [x.trader.name for x in Trade.objects.filter(round=round)]
    data = {
        'traders':traders
    }
    return JsonResponse(data)

def all_trades(request, market_id):
    round = request.GET['round_num']
    trades = Trade.objects.filter(round=round)
    market = Market.objects.get(market_id=market_id)
    alpha, beta, theta = market.alpha, market.beta, market.theta
    avg_price = sum([trade.unit_price for trade in trades]) / len(trades)

    traders = [x.trader.name for x in trades]
    profit = []
    for trade in trades:
        demand = alpha - beta*Decimal(trade.unit_price) + theta*Decimal(avg_price)
        expenses = trade.trader.prod_cost * trade.unit_amount
        income = trade.unit_price * min(demand,trade.unit_amount)
        trade_profit = income - expenses
        print(demand, expenses, income, trade_profit)
        profit.append(trade_profit)
        trade.trader.money += trade_profit
        trade.trader.save()

        new_stat = Stats(market=market,
                         trader=trade.trader,
                         round=round,
                         price=trade.unit_price,
                         amount=trade.unit_amount,
                         profit=trade_profit,
                         bank=trade.trader.money+trade_profit)
        new_stat.save()
    market.round += 1
    market.save()

    data = {
        'traders':traders,
        'profit':profit
    }
    return JsonResponse(data)

def current_round(request, market_id):
    market = Market.objects.get(market_id=market_id)
    data = {
        'round':market.round
    }
    return JsonResponse(data)

def download(request, market_id):
    market = Market.objects.get(market_id=market_id)
    market_traders = Trader.objects.filter(market=market)
    total_rounds = market.round
    data = "Round,Average price,Average amount,Average profit,"
    for trader in market_traders:
        data += trader.name + " bank,"
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
            data += str(trader_stats.bank) + ","
        data += "<br>"
    output = open(market.market_id + "_stats.csv", "w")
    output.write(data)
    output.close()
    return HttpResponse(data)
