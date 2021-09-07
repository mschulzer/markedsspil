from ..models import Trade, RoundStat, UnusedCosts, UsedCosts
from decimal import Decimal
from .factories import MarketFactory, TradeFactory, TraderFactory


### Test MarketModel ###
# All relevant properties are currently being tested in the test_factories test suite
    
### Test TraderModel ###
# Most relevant properties are currently being tested in the test_factories test suite

def test_prod_cost_algorithm(db):
    # We start out with a market and unused costs.
    market = MarketFactory()
    UnusedCosts.objects.create(
        market=market, cost=Decimal('20.00'))
    UnusedCosts.objects.create(
        market=market, cost=Decimal('30.00'))

    # There really are two unused costs at this point
    assert (UnusedCosts.objects.all().count() == 2)

    # We create a trader and call the production cost algorithm
    first_trader = TraderFactory(market=market)
    first_trader.prod_cost_algorithm()

    # There is now only one unused cost left
    assert (UnusedCosts.objects.all().count() == 1)

    # There is 1 used cost
    assert (UsedCosts.objects.all().count() == 1)

    # We create a second trader
    second_trader = TraderFactory(market=market)
    second_trader.prod_cost_algorithm()

    # There are now no unused costs left
    assert (UnusedCosts.objects.all().count() == 0)

    # There are 2 used costs
    assert (UsedCosts.objects.all().count() == 2)

    # We currently expect one trader with cost 20.00 an another with cost 30.00
    actual_set_of_trader_costs = {
        float(first_trader.prod_cost), float(second_trader.prod_cost)}
    expected_set_of_trader_costs = {20.00, 30.00}
    assert (actual_set_of_trader_costs == expected_set_of_trader_costs)

    # We create a third trader
    third_trader = TraderFactory(market=market)
    third_trader.prod_cost_algorithm()

    # The creating of the third trader should produce a new unused cost (30.00 + 20.00)/2. This cost will be assigned to the third trader
    # There is now no unused costs
    assert (UnusedCosts.objects.all().count() == 0)

    # There are 3 used costs
    assert (UsedCosts.objects.all().count() == 3)

    # We currently expect one trader with cost 20.00 an another with cost 30.00 and a third with 25.00
    actual_set_of_trader_costs = {
        float(first_trader.prod_cost), float(second_trader.prod_cost), float(third_trader.prod_cost)}
    expected_set_of_trader_costs = {20.00, 30.00, 25.00}
    assert (actual_set_of_trader_costs == expected_set_of_trader_costs)

    # We create a fourth trader
    fourth_trader = TraderFactory(market=market)
    fourth_trader.prod_cost_algorithm()

    # The creating of the fourth trader should produce a two new unused cost (20.00 + 25.00)/2 and (25.00+30.00)/2.
    # One of these new costs should be be assigned to the fourthtrader
    # There is now one unused costs
    assert (UnusedCosts.objects.all().count() == 1)

    # There are 4 used costs
    assert (UsedCosts.objects.all().count() == 4)

    # We produce a fifth trader
    fifth_trader = TraderFactory(market=market)
    fifth_trader.prod_cost_algorithm()

    # There should be 0 unused costs at this point
    assert (UnusedCosts.objects.all().count() == 0)

    # There should be  5 used costs
    assert (UsedCosts.objects.all().count() == 5)

    # We currently expect one trader with cost 20.00 an another with cost 30.00 and a third with 25.00
    actual_set_of_trader_costs = {
        float(first_trader.prod_cost),
        float(second_trader.prod_cost),
        float(third_trader.prod_cost),
        float(fourth_trader.prod_cost),
        float(fifth_trader.prod_cost)
    }
    # The set of assigned costs match our expectations
    expected_set_of_trader_costs = {20.00, 22.50, 25.00, 27.50, 30.00}
    assert (actual_set_of_trader_costs ==
                     expected_set_of_trader_costs)



### TradeModel ###
# Most properties are being tested in the test_factories test suite

def test_constraint_trader_and_round_unique_together(db):
    """ There can only be one trade pr trader pr round """
    trade = TradeFactory(round=17)    
    # we try to make a trade with same trader and same round - this
    # should cast an integrity error in the database

    try:
        Trade.objects.create(
            trader=trade.trader, round=17)
        error_mgs = "there was no error"
    except:
        error_mgs = "error message"
    finally:
        assert error_mgs == "error message"

def test_constraint_trade_and_round_unique_together_okay_to_update_trade(db):
    """ updating a trade will not cast an integrity error """
    trade = TradeFactory(round=17)
    try:
        trade.balance_after = 400
        trade.save()
        mgs = "there was no error"
    except:
        mgs = "error message"
    finally:
        assert mgs == "there was no error"
    trade.refresh_from_db()
    assert trade.balance_after == 400

### Test RoundStatModel ###

def test_object_creation_and_name(db):
    market = MarketFactory()
    r1 = RoundStat.objects.create(market=market, round=3, avg_price=Decimal('34.34')) 
    assert isinstance(r1, RoundStat)
    assert r1.market == market
    assert r1.round == 3
    assert r1.avg_price == Decimal('34.34')
    assert str(r1) == f"{market.market_id}[3]"

def test_market_and_round_uinque_together(db):
    """ There can only be one roundstat object pr market pr round """
    market1 = MarketFactory()
    market2 = MarketFactory()

    RoundStat.objects.create(
        market=market1, round=3, avg_price=34.343)

    # it should be possible to create another object with same market, but different round
    s1 = RoundStat.objects.create(market=market1, round=45, avg_price=34.343)
    assert isinstance(s1, RoundStat)

    # it should be possible to create another object with same same round, but different market
    s2 = RoundStat.objects.create(
        market=market2, round=3, avg_price=34.343)
    assert isinstance(s2, RoundStat)

    # it should not be possible to possible to create another object with same round and market
    try: 
        RoundStat.objects.create(
            market=market1, round=3, avg_price=100)
        mgs = "No error happend"
    except:
        mgs = "An error happened"
    finally:
        assert mgs == "An error happened"
