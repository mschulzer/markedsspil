import factory

from ..models import Market, Trader, Trade
from django.contrib.auth import get_user_model
from decimal import Decimal


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    
    username = factory.Sequence(lambda n: 'john%s' % n)
    email = 'JohnDoe@example.com'
    password = factory.PostGenerationMethodCall('set_password',
                                                'defaultpassword')


class MarketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Market 

    product_name_singular = 'baguette'
    product_name_plural = 'baguettes'
    initial_balance = Decimal('5000.00')
    alpha = Decimal('105.0000')
    beta = Decimal('17.5000')
    theta = Decimal('14.5800')
    min_cost = Decimal('8.00')
    max_cost = Decimal('8.00')
    created_by = factory.SubFactory(UserFactory)
    max_rounds = 15
    endless = False


class TraderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trader
    market = factory.SubFactory(MarketFactory)
    name = factory.Sequence(lambda n: 'eva%s' % n)
    balance = Decimal('4734.23')
    prod_cost = Decimal('8.00')
    round_joined = 0

def round_to_int(number):
    """ Re-naming is needed since 'round' is also the name of a field in TradeFactory """
    return round(number)

class TradeFactory(factory.django.DjangoModelFactory):
    """ Produces a regular trade that has been processed (after host has finished round) """
    class Meta:
        model = Trade
    
    trader = factory.SubFactory(TraderFactory)
    unit_price = Decimal('10.20')
    unit_amount = 13
    demand = max(0, round_to_int(MarketFactory.alpha - MarketFactory.beta*unit_price  + MarketFactory.theta * Decimal('12.32'))) # 12.32 is stand in for market avg. prce 
    units_sold = min(demand, unit_amount) 
    profit = Decimal(units_sold * unit_price - unit_amount * TraderFactory.prod_cost)
    balance_after = Decimal(TraderFactory.balance) + profit
    balance_before = Decimal(TraderFactory.balance)
    round = 37

class UnProcessedTradeFactory(factory.django.DjangoModelFactory):
    """ Produces a regular trade that has not been processed (before host has finished round) """     
    class Meta:
        model = Trade

    trader = factory.SubFactory(TraderFactory)
    unit_price = Decimal('10.20')
    unit_amount = 13
    round = 37
    balance_before = Decimal(TraderFactory.balance)


class ForcedTradeFactory(factory.django.DjangoModelFactory):
    """ 
    Produces a forced trade 
    Note that balance_after and balance_before is set to None by default. Sometimes balance_after and balance_before should be set equal to trader.balance
     """
    class Meta:
        model = Trade

    trader = factory.SubFactory(TraderFactory)
    was_forced = True
    balance_after = None
    balance_before = None
    round = 37
