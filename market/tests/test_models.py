from django.test import TestCase
from ..models import Market, Trader, Trade, RoundStat
from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal 
class MarketModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        User = get_user_model()
        cls.test_user = User.objects.create_user(
            username='kris',
            password='testpass123',
        )
        cls.market = Market.objects.create(
            initial_balance=4000.123123,
            alpha=102.20341111,
            beta=304.50035, 
            theta=14.1234, 
            min_cost=6, 
            max_cost=20.13, 
            product_name_singular="x",
            product_name_plural='xs',
            created_by=cls.test_user)

    
    def test_saving_markets(self):
        saved_markets = Market.objects.all()
        self.assertEqual(saved_markets.count(), 1)
        market = saved_markets.first()
        self.assertIsInstance(market, Market)
        self.assertEqual(market.alpha, Decimal('102.2034'))
        self.assertEqual(market.beta, Decimal('304.5004'))
        self.assertEqual(market.theta, Decimal('14.1234'))
        self.assertEqual(market.min_cost, Decimal('6.00'))
        self.assertEqual(market.max_cost, Decimal('20.13'))
        self.assertEqual(market.round, 0)
        self.assertEqual(market.initial_balance, Decimal('4000.12'))
        self.assertEqual(market.created_by, self.test_user)

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
        expected_object_name = f"{self.market.market_id}[0]:102.2034,304.5004,14.1234"
        market = Market.objects.first()
        self.assertEqual(str(market), expected_object_name)
 


class TraderModelTest(TestCase):

    @classmethod
    def setUp(self):
        self.market = Market.objects.create(
            initial_balance='4000.12',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6.01, max_cost=20.23)

        self.market = Market.objects.first()
        self.trader = Trader.objects.create(
            market=self.market, name='Stefan', prod_cost=20.23, balance=4000.12)
        self.trader = Trader.objects.first()
        
    def test_saving_traders(self):

        saved_traders = Trader.objects.all()
        self.assertEqual(saved_traders.count(), 1)
        self.assertIsInstance(self.trader, Trader)
        self.assertEqual(self.trader.market, self.market)
        self.assertEqual(self.trader.name, 'Stefan')
        self.assertEqual(self.trader.prod_cost, Decimal('20.23'))
        self.assertEqual(self.trader.balance, Decimal('4000.12'))

               
    def test_object_name(self):  
        expected_object_name = f"Stefan [{self.market.market_id}] - ${self.market.initial_balance}"
        self.assertEqual(str(self.trader), expected_object_name)
    
    def test_is_ready_is_false(self):
        self.assertFalse(self.trader.is_ready()) 
        
    def test_is_ready_is_true(self):
        Trade.objects.create(trader=self.trader, round=self.trader.market.round)
        self.assertTrue(self.trader.is_ready())

    def test_is_ready_is_no_longer_true(self):
        Trade.objects.create(trader=self.trader, round=self.trader.market.round)
        self.market.round = 17
        self.market.save()
        self.market.refresh_from_db()
        self.trader.refresh_from_db()
        self.assertFalse(self.trader.is_ready())      

class TradeModelTest(TestCase):
    
    def test_object_name(self):
        market = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman', balance=400)
        trade = Trade.objects.create(
        trader= trader, round=market.round, unit_price=13.45, unit_amount=34, profit=-4, balance_after=-400, was_forced=False)

        expected_object_name = f"Joe Salesman $13.45 x 34 [{market.market_id}][5]"
        self.assertEqual(str(trade), expected_object_name)
    
       
    def test_constraint_trader_and_round_unique_together(self):
        market = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman', balance=30)

        # we try to make a trade with same trader and same round - this should cast an integrety error in the database
    
        Trade.objects.create(
            trader=trader, round=market.round, unit_price=4, unit_amount=434)
        try:
            Trade.objects.create(
                trader=trader, round=market.round, unit_price=4, unit_amount=434)
            error_mgs = "there was no error"
        except:
            error_mgs = "error message"
        finally:
            self.assertEqual(error_mgs, "error message")
    
    def test_constraint_trade_and_round_unique_together_okay_to_update_trade(self):
        market = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman', balance=4)

        # we try to make a trade with same trader and same round - this should cast an integrety error in the database
    
        trade = Trade.objects.create(
            trader=trader, round=market.round, unit_price=4, unit_amount=434)
        trade.balance_after = 400
        trade.save()

from decimal import Decimal 
class TestRoundStatModel(TestCase):

    def test_object_creation_and_name(self):
        market = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        roundstat = RoundStat.objects.create(market=market, round=3, avg_price=34.3433) 
        r1 = RoundStat.objects.first()
        self.assertIsInstance(r1, RoundStat)
        self.assertEqual(r1.market, market)
        self.assertEqual(r1.round, 3)
        self.assertEqual(r1.avg_price, Decimal('34.34'))
        self.assertEqual(str(r1), f"{market.market_id}[3]")


    def test_market_and_round_uinque_together(self):
        market1 = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        market2 = Market.objects.create(
            initial_balance='4000',
            alpha=102.2034, beta=304.5003, theta=14.1234, min_cost=6, max_cost=20, round=5)
        RoundStat.objects.create(
            market=market1, round=3, avg_price=34.343)

        # it should be possible to create another object with same market, but different round
        s1 = RoundStat.objects.create(market=market1, round=4, avg_price=34.343)
        self.assertIsInstance(s1, RoundStat)

        # it should be possible to create another object with same same round, but different market
        s1 = RoundStat.objects.create(
            market=market2, round=3, avg_price=34.343)
        self.assertIsInstance(s1, RoundStat)

        # it should not be possible to possible to create another object with same round and market
        try: 
            RoundStat.objects.create(
                market=market1, round=3, avg_price=100)
        except:
            mgs = "this should execute"
        finally:
            self.assertEqual(mgs, "this should execute")



           
