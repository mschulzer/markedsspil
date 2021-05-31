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
    
    def test_is_ready_is_false(self):
        self.assertFalse(self.trader.is_ready()) 
        
    def test_is_ready_is_true(self):
        Trade.objects.create(trader=self.trader)
        self.assertTrue(self.trader.is_ready())

    def test_is_ready_is_no_longer_true(self):
        Trade.objects.create(trader=self.trader)
        self.market.round += 1
        self.assertFalse(self.trader.is_ready())      


class TradeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.market = Market.objects.create(round=5)
        cls.trader = Trader.objects.create(market=cls.market, name='Joe Salesman')
        cls.trade = Trade.objects.create(trader=cls.trader, unit_price=13.45, unit_amount=34)
   
    def test_trade_object_creation(self):
        self.assertIsInstance(self.trade, Trade)
        self.assertEqual(self.trade.market, self.market)
        self.assertEqual(self.trade.round, self.market.round)

    def test_object_name(self):
        expected_object_name = f"Joe Salesman $13.45 x 34 [{self.market.market_id}][5]"
        self.assertEqual(str(self.trade), expected_object_name)
        
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
    
        with self.assertRaises(Exception):
            Trade.objects.create(
                round=0, trader=trader)

        with self.assertRaises(Exception):
            Trade.objects.create(
                round=0, market=market, trader=trader)


    def test_specifying_round_num_is_allowed_when_trade_is_forced(self):
        market = Market.objects.create(round=1)
        trader = Trader.objects.create(market=market, name='KomForSent')

        Trade.objects.create(
            trader=trader, round=0, was_forced=True)
        
        new_trade = Trade.objects.get(trader=trader)
        self.assertEqual(new_trade.trader.name, 'KomForSent')
        self.assertEqual(new_trade.round, 0)

        market.round = 18 
        market.save()

        Trade.objects.create(
            trader=trader, round=8, was_forced=True)

        new_trade = Trade.objects.get(trader=trader, round=8)
        self.assertEqual(new_trade.trader.name, 'KomForSent')
        self.assertEqual(new_trade.round, 8)
