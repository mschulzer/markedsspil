from django.test import TestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve
from .factories import TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory, TraderFactory, UserFactory, MarketFactory
from ..models import Market, Trader, Trade, RoundStat
from decimal import Decimal


class TestUserFactory(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.user = UserFactory()

    def test_sanity_check(self):
        self.assertIsInstance(self.user, get_user_model())
        self.assertTrue('john' in self.user.username)

    def test_can_log_in(self):
        is_logged_in = self.client.login(username=self.user.username, password='defaultpassword')
        self.assertTrue(is_logged_in)


class TestMarketFactory(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.market = MarketFactory()
    
    def test_default_round_is_zero(self):
        self.assertEqual(self.market.round, 0)

    def test_market_id_created_properly(self):
        self.assertIsInstance(self.market.market_id, str)
        self.assertEqual(len(self.market.market_id), 8)

    def test_instances_of_default_factory_market(self):
        self.assertIsInstance(self.market, Market)
        self.assertIsInstance(self.market.created_by, get_user_model())
        self.assertIsInstance(self.market.alpha, Decimal)
        self.assertIsInstance(self.market.beta, Decimal)
        self.assertIsInstance(self.market.theta, Decimal)
        self.assertIsInstance(self.market.initial_balance, Decimal)
        self.assertIsInstance(self.market.max_cost, Decimal)
        self.assertIsInstance(self.market.min_cost, Decimal)
        self.assertIsInstance(self.market.round, int)
        self.assertIsInstance(self.market.max_rounds, int)
        self.assertIsInstance(self.market.endless, bool)

    def test_factory_with_provided_values(self):
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
            endless=True
        )
        self.assertEqual(market.alpha, Decimal('102.2034'))
        self.assertEqual(market.beta, Decimal('304.5003'))
        self.assertEqual(market.theta, Decimal('14.1234'))
        self.assertEqual(market.product_name_singular, 'cake')
        self.assertEqual(market.product_name_plural, 'cakes')
        self.assertEqual(market.initial_balance, Decimal('4000.00'))
        self.assertEqual(market.max_cost, Decimal('6.30'))
        self.assertEqual(market.min_cost, Decimal('4.00'))
        self.assertEqual(market.created_by.username, 'egon')
        self.assertEqual(market.round, 74)
        self.assertEqual(market.endless, True)

        # object name
        expected_object_name = f"{market.market_id}[74]:102.2034,304.5003,14.1234"
        self.assertEqual(str(market), expected_object_name)
    
    def test_saving_existing_market_does_not_create_new_market_or_new_market_id(self):
        market = MarketFactory()
        expected_market_id = market.market_id
        expected_num_markets = Market.objects.all().count()
        market.save()
        actual_num_markets = Market.objects.all().count() 
        self.assertEqual(expected_num_markets, actual_num_markets )
        self.assertEqual(expected_market_id, market.market_id)
 
    def test_game_over_method_1(self):
        market = MarketFactory(round=5, max_rounds=5)
        self.assertTrue(market.game_over())

    def test_game_over_method_2(self):
        market = MarketFactory(round=5, max_rounds=6)
        self.assertFalse(market.game_over())


class TestTraderFactory(TestCase):
    
    def test_default_trader_factory_with_default_values(self):
        trader = TraderFactory()
        self.assertIsInstance(trader, Trader)
        self.assertTrue('eva' in trader.name)
        self.assertIsInstance(trader.market, Market)
        self.assertFalse(trader.is_ready()) # trader has not made a trade in current round, so is not "ready"
        self.assertIsInstance(trader.balance, Decimal)
        self.assertIsInstance(trader.prod_cost, Decimal)


    def test_trader_factory_ith_provided_values(self):
        market = MarketFactory(round=17)
        trader = TraderFactory(
            market=market,
            prod_cost=Decimal('4.30'), 
            balance=Decimal('8.00'), 
            name='John'
        )
        self.assertEqual(trader.name, 'John')
        self.assertEqual(trader.balance, Decimal('8.00'))
        self.assertEqual(trader.prod_cost, Decimal('4.30'))
        self.assertEqual(trader.market.round, 17)
        self.assertEqual(str(trader), f"John [{market.market_id}] - $8.00")

    def test_trader_is_ready(self):
        """ A trader is ready if (and only if) he has made a trade in current round """
        trader = TraderFactory()
        trader.market.round = 19
        self.assertFalse(trader.is_ready())
        
        TradeFactory(trader=trader, round=17)
        self.assertFalse(trader.is_ready())

        TradeFactory(trader=trader, round=19)
        self.assertTrue(trader.is_ready())


class TestTradeFactory(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.trade = TradeFactory()

    def test_trade_factory_with_default_values(self):
        self.assertIsInstance(self.trade, Trade)
        self.assertEqual(self.trade.unit_amount, 13)
        self.assertIsInstance(self.trade.trader, Trader)
        self.assertIsInstance(self.trade.profit, Decimal)
        self.assertFalse(self.trade.was_forced)
    
    def test_trade_factory_with_provided_values(self):
        trader=TraderFactory(name='bobby')
        trade = TradeFactory(trader=trader, round=3, unit_price=Decimal('4.50'), unit_amount=17)
        self.assertEqual(trade.round,3)
        self.assertEqual(str(trade), f"bobby $4.50 x 17 [{trader.market.market_id}][3]")

class TestUnProcessedTradeFactory(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.trade = UnProcessedTradeFactory()
        market = cls.trade.trader.market
      
 
    def test_basics(self):
        self.assertIsInstance(self.trade, Trade)
        self.assertEqual(self.trade.unit_amount, 13)
        self.assertEqual(self.trade.profit, None)

class TestForcedTradeFactory(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.trade = ForcedTradeFactory()

    def test_basics(self):
        self.assertIsInstance(self.trade, Trade)
        self.assertTrue(self.trade.was_forced)
        self.assertEqual(self.trade.unit_amount, None)
        self.assertEqual(self.trade.unit_price, None)
        self.assertEqual(self.trade.profit, None)

