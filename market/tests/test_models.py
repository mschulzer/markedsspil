from django.test import TestCase
from ..models import Market, Trader, Trade

class MarketModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create(
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20
        )
    
    def test_saving_markets(self):
        saved_markets = Market.objects.all()
        self.assertEqual(saved_markets.count(), 1)
        self.assertIsInstance(self.market, Market)
        self.assertEqual(self.market.alpha, 102.2034)
        self.assertEqual(self.market.beta, 304.5003)
        self.assertEqual(self.market.theta, 14.1234)
        self.assertEqual(self.market.min_cost, 6)
        self.assertEqual(self.market.max_cost, 20)
        self.assertEqual(self.market.round, 0)

    def test_market_id_is_good(self):
        self.assertEqual(len(self.market.market_id), 8)
        self.assertTrue(type(self.market.market_id) is str)

    def test_saving_existing_market_does_not_create_new_market_id(self):
        market_id = self.market.market_id
        self.assertEqual(Market.objects.all().count(), 1)
        self.market.save()
        self.assertEqual(market_id, self.market.market_id)
        self.assertEqual(Market.objects.all().count(), 1)

    def test_object_name(self):
        expected_object_name = f"{self.market.market_id}[0]:102.2034,304.5003,14.1234"
        self.assertEqual(str(self.market), expected_object_name)


class TraderModelTest(TestCase):

    @classmethod
    def setUp(self):
        self.market = Market.objects.create()
        self.trader = Trader.objects.create(
            market=self.market, name='Stefan', prod_cost=2)

    def test_saving_traders(self):
        saved_traders = Trader.objects.all()
        self.assertEqual(saved_traders.count(), 1)
        self.assertIsInstance(self.trader, Trader)
        self.assertEqual(self.trader.market, self.market)
        self.assertEqual(self.trader.name, 'Stefan')
        self.assertEqual(self.trader.prod_cost, 2)
        self.assertEqual(self.trader.balance, Trader.initial_balance)

               
    def test_object_name(self):  
        expected_object_name = f"Stefan [{self.market.market_id}] - $5000"
        self.assertEqual(str(self.trader), expected_object_name)


class TradeModelTest(TestCase):
   
    def test_trade_object_creation(self):
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman')
        trade = Trade.objects.create(trader=trader)
        self.assertIsInstance(trade, Trade)
        self.assertEqual(trade.market, market)
        self.assertEqual(trade.round, market.round)

    def test_object_name(self):
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman')
        trade = Trade.objects.create(trader=trader, unit_price=13.45, unit_amount=34)

        expected_object_name = f"Joe Salesman $13.45 x 34 [{market.market_id}]"
        self.assertEqual(str(trade), expected_object_name)
        
    def test_raises_error_when_creating_a_trade_with_forbidden_kwargs(self):
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name='Joe Salesman')
        Trade.objects.create(
            trader=trader)

        with self.assertRaises(Exception):
            Trade.objects.create(
                market=market, trader=trader)
        with self.assertRaises(Exception):
            Trade.objects.create(
                round=4, trader=trader)

