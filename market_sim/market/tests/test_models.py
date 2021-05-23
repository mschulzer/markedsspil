from django.test import TestCase
from ..models import Market, Trader, Trade, Stats

class MarketModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create(
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=2)
    
    def test_saving_markets(self):
        saved_markets = Market.objects.all()
        self.assertEqual(saved_markets.count(), 1)
        self.assertIsInstance(self.market, Market)
        self.assertEqual(self.market.alpha, 102.2034)

    def test_saving_markets_with_default_params(self):
        new_market = Market.objects.create()
        self.assertEqual(new_market.alpha, 105.0000)
        saved_markets = Market.objects.all()
        self.assertEqual(saved_markets.count(), 2)

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
        expected_object_name = f"{self.market.market_id}[2]:102.2034,304.5003,14.1234"
        self.assertEqual(str(self.market), expected_object_name)


class TraderModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader = Trader.objects.create(
            market=cls.market, name='Stefan', money=15, prod_cost=2)

    def test_saving_traders(self):
        saved_traders = Trader.objects.all()
        self.assertEqual(saved_traders.count(), 1)
        self.assertIsInstance(self.trader, Trader)
        self.assertEqual(self.trader.money,15)

    def test_saving_trader_with_default_params(self):
        new_trader = Trader.objects.create(market=self.market, name='Otto Leisner')
        self.assertEqual(new_trader.money, 0)
        saved_traders = Trader.objects.all()
        self.assertEqual(saved_traders.count(), 2)
        
    def test_object_name(self):  
        expected_object_name = f"Stefan [{self.market.market_id}] - $15"
        self.assertEqual(str(self.trader), expected_object_name)


class TradeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader = Trader.objects.create(market=cls.market, name='Joe Salesman', money=20, prod_cost=5)
        cls.trade = Trade.objects.create(market=cls.market, trader=cls.trader, unit_price=13.45, unit_amount=34, round=4)

    def test_saving_trades(self):
        saved_trades = Trade.objects.all()
        self.assertEqual(saved_trades.count(), 1)
        self.assertIsInstance(self.trade, Trade)
        self.assertEqual(self.trade.unit_price, 13.45)

    def test_saving_trade_with_default_params(self):
        new_trade = Trade.objects.create(market=self.market, trader=self.trader, unit_price=4)
        self.assertEqual(new_trade.round, 0)
        saved_trades = Trade.objects.all()
        self.assertEqual(saved_trades.count(), 2)
        
    def test_object_name(self):
        expected_object_name = f"Joe Salesman $13.45 x 34 [{self.market.market_id}]"
        self.assertEqual(str(self.trade), expected_object_name)


class StatsModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader = Trader.objects.create(market=cls.market, name='Joe Salesman')
        cls.stats = Stats(market=cls.market, trader=cls.trader, round=4, price=45.3431, amount=55, profit=1.2345, bank=5)
        cls.stats.save()

    def test_saving_stats(self):
        saved_stats = Stats.objects.all()
        self.assertEqual(saved_stats.count(), 1)
        self.assertIsInstance(self.stats, Stats)
        self.assertEqual(self.stats.amount, 55)
        self.assertEqual(self.stats.trader.name, 'Joe Salesman')


