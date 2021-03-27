from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Market, Trader

def index(request):
    template = loader.get_template('market/index.html')
    return HttpResponse(template.render({}, request))

def join(request):
    try:
        market = get_object_or_404(Market, market_id=request.POST['market_id'])
        new_trader = market.trader_set.create(name=request.POST['username'])
    except (KeyError, Market.DoesNotExist):
        return render(request, 'market/index.html', {})
    else:
        new_trader.save()
        return HttpResponseRedirect(reverse('market:play', args=(market.market_id,)))

def play(request, market_id):
    try:
        market = get_object_or_404(Market, market_id=market_id)
        #trader = get_object_or_404(Trader, name=username)
    except:
        return render(request, 'market/index.html', {})
    else:
        return HttpResponse("hej :)")

def sell(request, market_id):
    HttpResponse("Not implemented yet :)")
