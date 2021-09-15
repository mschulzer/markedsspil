"""
To only run the tests in this file:
$ docker-compose run web pytest market/tests/test_functional.py
"""
from ..models import Market, Trader, Trade
from django.urls import reverse
from .factories import TraderFactory, MarketFactory, TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory


## Two player game
def test_round_0_one_forced_move(logged_in_user, client):

    # A teacher creates a market
    post_data = {
        'product_name_singular':'baguette',
        'product_name_plural': 'baguettes',
        'initial_balance':4000,
        'alpha': 21.402, 
        'beta': 44.2,
        'theta': 2.0105, 
        'min_cost': 11, 
        'max_cost': 144,
        'max_rounds': 15,
        'endless': False}
    client.post(
        reverse('market:create'), 
        post_data
    )
    assert Market.objects.all().count() == 1

    market = Market.objects.all().first()

    assert market.created_by == logged_in_user

    # A player named Marianne joins the market:
    client.post(
        reverse('market:join'),
        {
            'name': 'Marianne',
            'market_id': market.market_id,
        }
    )
    assert Trader.objects.all().count() == 1


    marianne = Trader.objects.get(name='Marianne')

    # Marianne makes a trade:
    post_data = {
        'unit_price': '10.9', 
        'unit_amount': '45'
        }

    client.post(reverse('market:play', args=(market.market_id,)), post_data)

    trade1 = Trade.objects.first()

    # let's assert that the trade was not forced and that the player is ready
    assert not trade1.was_forced
    assert marianne.is_ready()

    # Now a player called Klaus joins the game
    client.post(
        reverse('market:join'),
        {
            'name': 'Klaus',
            'market_id': market.market_id,
        }    
    )

    klaus = Trader.objects.get(name='Klaus')

    # Since market.min_cost = 11 < market.max_cost = 144, we expect
    # one trader to have prod_cost = 11 and the other to have prod_cost = 144
    actual_set_of_trader_costs = {float(marianne.prod_cost), float(klaus.prod_cost)}
    expected_set_of_trader_costs = {11.00, 144.00}
    assert (actual_set_of_trader_costs == expected_set_of_trader_costs)


    
    # Klaus has not made a trade yet so let's assert that klaus it not ready at this point        
    assert not klaus.is_ready()

    # Even though Klaus is not ready, the teacher chooses to proceed to the next round:
    url = reverse('market:monitor', args=(market.market_id,))
    client.post(url)

    # There should now be 2 trades in the database & Klaus trade should be forced
    assert Trade.objects.all().count() == 2
    klaus_trade=Trade.objects.get(trader=klaus)
    assert klaus_trade.was_forced

    # Mariannes profit and balance_after should now be set in her trade
    mariannes_trade = Trade.objects.get(trader=marianne)
    assert mariannes_trade.profit is not None
    assert mariannes_trade.balance_after is not None

    # Mariannes current balance should be equal to the balance set in her recent trade
    marianne = Trader.objects.get(name='Marianne')
    assert mariannes_trade.balance_after == marianne.balance

    # we are now in round 1
    market = Market.objects.first()
    assert market.round == 1


def test_round_1_one_forced_move(logged_in_user, client):
    """ Established the state obtained at the end of the test above. Proceeds to test round 1 behaviour """

    market = MarketFactory(round=1, created_by=logged_in_user)
    marianne = TraderFactory(market=market, name="Marianne")
    klaus = TraderFactory(market=market, name="Klaus", balance=324)

    # Historical round zero trades
    m0 = TradeFactory(trader=marianne, round=0)
    k0 = ForcedTradeFactory(trader=klaus, round=0)

    # Marianne makes a trade decision in round 1 (it is not processed yet, so most field should be None)
    m1= UnProcessedTradeFactory(trader=marianne, round=1)
    assert m1.profit is None

    # Mariannes trade was not forced. Marianne is ready, but Klaus is not
    assert not m1.was_forced
    assert marianne.is_ready()
    assert not klaus.is_ready()

    # Even though Klaus is not ready, the teacher chooses to proceed to the next round:
    url = reverse('market:monitor', args=(market.market_id,))
    client.post(url)

    # Klaus' balance has not changed
    assert klaus.balance == 324

    # a forced trade has been made for Klaus
    klaus_trade = Trade.objects.get(
        trader=klaus, round=1)   # we are now in round 1
    assert klaus_trade.was_forced

    # mariannes trade has been processed, so the profit has been calculated
    m1.refresh_from_db()
    assert m1.profit is not None

    # we are now in round 2
    market.refresh_from_db()
    assert market.round == 2
