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

    def test_instances(self):
        self.assertIsInstance(self.market, Market)
        self.assertIsInstance(self.market.created_by, get_user_model())

    def test_alpha(self):
        self.assertIsInstance(self.market.alpha, Decimal)
        self.assertEqual(self.market.alpha, 105.00)

    def test_non_default_round(self):
        market = MarketFactory(round=4)
        self.assertEqual(market.round, 4)

class TestTraderFactory(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.trader = TraderFactory()

    def test_basics(self):
        self.assertIsInstance(self.trader, Trader)
        self.assertTrue('eva' in self.trader.name)
        self.assertIsInstance(self.trader.market, Market)


class TestTradeFactory(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by multiple test methods in class
        cls.trade = TradeFactory()

    def test_basics(self):
        self.assertIsInstance(self.trade, Trade)
        self.assertEqual(self.trade.unit_amount, 13)
        self.assertIsInstance(self.trade.trader, Trader)
        self.assertFalse(self.trade.was_forced)
    
    def test_non_default_round(self):
        trade = TradeFactory(round=3)
        self.assertEqual(trade.round,3)

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
