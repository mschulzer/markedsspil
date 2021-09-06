from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from .factories import TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory, TraderFactory, UserFactory, MarketFactory
from ..models import Market, Trader, Trade, RoundStat
from decimal import Decimal


import pytest

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def market(db):
    return MarketFactory()

@pytest.fixture
def trade(db):
    return TradeFactory()

### Test UserFactory ###

def test_sanity_check(user, db):
    assert isinstance(user, get_user_model())
    assert 'john' in user.username

def test_can_log_in(client, user, db):
    is_logged_in = client.login(username=user.username,
                                password='defaultpassword')
    assert is_logged_in

### Test MarketFactory ###

def test_default_round_is_zero(market):
    assert market.round == 0

def test_market_id_created_properly(market):
    assert isinstance(market.market_id, str)
    assert len(market.market_id) == 8

def test_instances_of_default_factory_market(market):
    assert isinstance(market, Market)
    assert isinstance(market.created_by, get_user_model())
    assert isinstance(market.alpha, Decimal)
    assert isinstance(market.beta, Decimal)
    assert isinstance(market.theta, Decimal)
    assert isinstance(market.initial_balance, Decimal)
    assert isinstance(market.max_cost, Decimal)
    assert isinstance(market.min_cost, Decimal)
    assert isinstance(market.round, int)
    assert isinstance(market.max_rounds, int)
    assert isinstance(market.endless, bool)

def test_factory_with_provided_values(db):
    market = MarketFactory(
        alpha=Decimal('102.2034'), 
        beta=Decimal('304.5003'), 
        theta=Decimal('14.1234'),
        product_name_singular ='cake',
        product_name_plural = 'cakes',
        min_cost=Decimal('4.00'),
        max_cost=Decimal('6.30'),
        initial_balance = Decimal('4000.00'),
        created_by = UserFactory(username='egon'),
        round=74,
        endless = True,
    )
    assert market.alpha == Decimal('102.2034')
    assert market.beta == Decimal('304.5003')
    assert market.theta == Decimal('14.1234')
    assert market.product_name_singular == 'cake'
    assert market.product_name_plural == 'cakes'
    assert market.initial_balance == Decimal('4000.00')
    assert market.max_cost == Decimal('6.30')
    assert market.min_cost == Decimal('4.00')
    assert market.created_by.username == 'egon'
    assert market.round == 74
    assert market.endless

    # object name
    expected_object_name = f"{market.market_id}[74]:102.2034,304.5003,14.1234"
    assert str(market) == expected_object_name

def test_saving_existing_market_does_not_create_new_market_or_new_market_id(db):
    market = MarketFactory()
    expected_market_id = market.market_id
    expected_num_markets = Market.objects.all().count()
    market.save()
    actual_num_markets = Market.objects.all().count() 
    assert expected_num_markets == actual_num_markets
    assert expected_market_id == market.market_id

def test_game_over_method_1(db):
    market = MarketFactory(round=5, max_rounds=5, endless=False)
    assert (market.game_over())

def test_game_over_method_1(db):
    market = MarketFactory(round=29, max_rounds=5, endless=False)
    assert (market.game_over())

def test_game_over_method_2(db):
    market = MarketFactory(round=5, max_rounds=5, endless=True)
    assert not (market.game_over())

def test_game_over_method_3(db):
    market = MarketFactory(round=5, max_rounds=6, endless=False)
    assert not (market.game_over())

def test_game_over_method_4(db):
    market = MarketFactory(round=5, max_rounds=6, endless=True)
    assert not (market.game_over())
    

### Test TraderFactory ###
def test_default_trader_factory_with_default_values(db):
    trader = TraderFactory()
    assert isinstance(trader, Trader)
    assert 'eva' in trader.name
    assert isinstance(trader.market, Market)
    assert not trader.is_ready() # trader has not made a trade in current round, so is not "ready"
    assert isinstance(trader.balance, Decimal)
    assert isinstance(trader.prod_cost, Decimal)

def test_trader_factory_ith_provided_values(db):
    market = MarketFactory(round=17)
    trader = TraderFactory(
        market=market,
        prod_cost=Decimal('4.30'), 
        balance=Decimal('8.00'), 
        name='John',
        round_joined=20,
    )
    assert trader.name == 'John'
    assert trader.balance == Decimal('8.00')
    assert trader.prod_cost == Decimal('4.30')
    assert trader.market.round == 17
    assert str(trader) == f"John [{market.market_id}] - $8.00"
    assert trader.round_joined == 20

def test_trader_is_ready(db):
    """ A trader is ready if (and only if) he has made a trade in current round """
    trader = TraderFactory()
    trader.market.round = 19
    assert not trader.is_ready()

    TradeFactory(trader=trader, round=17)
    assert not trader.is_ready()

    TradeFactory(trader=trader, round=19)
    assert trader.is_ready()

### Test TradeFactory ###
def test_trade_factory_with_default_values(trade):
    assert isinstance(trade, Trade)
    assert trade.unit_amount == 13
    assert isinstance(trade.trader, Trader)
    assert isinstance(trade.profit, Decimal)
    assert not trade.was_forced

def test_trade_factory_with_provided_values(db):
    trader = TraderFactory(name='bobby')
    trade = TradeFactory(trader=trader, round=3, unit_price=Decimal('4.50'), unit_amount=17)
    assert trade.round == 3
    assert str(trade) == f"bobby $4.50 x 17 [{trader.market.market_id}][3]"

### Test UnProcessedTradeFactory ###
def test_unprocessed_trade_factory_basics(db):
    trade = UnProcessedTradeFactory()
    assert isinstance(trade, Trade)
    assert trade.unit_amount == 13
    assert trade.profit is None

###  Test ForcedTradeFactory ###
def test_forced_trade_factory_basics(db):
    trade = ForcedTradeFactory()
    assert isinstance(trade, Trade)
    assert trade.was_forced
    assert trade.unit_amount is None
    assert trade.unit_price is None
    assert trade.profit is None

