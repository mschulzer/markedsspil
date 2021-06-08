from django.test import TestCase
from ..models import Market, Trader, Trade, RoundStat

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

    def test_alpha_will_be_saved_with_max_4_decimals(self):
        """ alpha is defined in the model have 4 decimal places """
        market = Market.objects.create(alpha=0.11112222)
        market.refresh_from_db()
        self.assertEqual(float(market.alpha), 0.1111)

    def test_alpha_will_be_saved_with_max_4_decimals_test_2(self):
        """ alpha is defined in the model have 4 decimal places """
        market = Market.objects.create(alpha=0.11118)
        market.refresh_from_db()
        self.assertEqual(float(market.alpha), 0.1112)


    def test_alpha_will_be_saved_with_max_4_decimals_test_3(self):
        """ alpha is defined in the model have 4 decimal places """
        market = Market.objects.create(alpha=23.1111111)
        market.refresh_from_db()
        self.assertEqual(float(market.alpha), 23.1111)

    def test_alpha_max_num_digits_test_1(self):
        """ 
        Max_num_digits is set to 10 & decimalplaces to 4. 
        This means that 999999.9999 is the largest value of alpha, we can save
        """
        market = Market.objects.create(alpha=999999.999912)
        market.refresh_from_db()
        self.assertEqual(float(market.alpha), 999999.9999)


    def test_alpha_max_num_digits_test_1(self):
        """ 
        Max_num_digits is set to 10 & decimalplaces to 4. 
        Trying to set alpha to one million ill through an error
        """
        try:
            market = Market.objects.create(alpha=1000000)
            market.refresh_from_db()
            error_message = "no error"
        except:
            error_message = "above was not possible"
        finally:
            self.assertEqual(error_message, "above was not possible")


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
        expected_object_name = f"Stefan [{self.market.market_id}] - ${Trader.initial_balance}"
        self.assertEqual(str(self.trader), expected_object_name)
    
    def test_is_ready_is_false(self):
        self.assertFalse(self.trader.is_ready()) 
        
    def test_is_ready_is_true(self):
        Trade.objects.create(trader=self.trader, round=self.trader.market.round)
        self.assertTrue(self.trader.is_ready())

    def test_is_ready_is_no_longer_true(self):
        Trade.objects.create(trader=self.trader, round=self.trader.market.round)
        self.market.round += 1
        self.assertFalse(self.trader.is_ready())      

class TradeModelTest(TestCase):
    
    def test_object_name(self):
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman')
        trade = Trade.objects.create(
        trader= trader, round=market.round, unit_price=13.45, unit_amount=34, profit=-4, balance_after=-400, was_forced=False)

        expected_object_name = f"Joe Salesman $13.45 x 34 [{market.market_id}][5]"
        self.assertEqual(str(trade), expected_object_name)
    
       
    def test_constraint_trader_and_round_unique_together(self):
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman')

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
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market, name='Joe Salesman')

        # we try to make a trade with same trader and same round - this should cast an integrety error in the database
    
        trade = Trade.objects.create(
            trader=trader, round=market.round, unit_price=4, unit_amount=434)
        trade.balance_after = 400
        trade.save()

    def test_decimals_are_floored_to_integer_on_object_creation(self):
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name='Joe Salesman')

        trade = Trade.objects.create(
            trader=trader,     
            unit_price = 0,
            unit_amount = 0,
            round = 0,
            was_forced = False,
            units_sold = 3.9,
            profit = 100,
            balance_after = 10
        )
        trade.refresh_from_db()
        self.assertEqual(trade.units_sold, 3)

    def test_constraint_error_when_saving_object_with_negative_units_sold(self):
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name='Joe Salesman')
        try:
            Trade.objects.create(trader=trader, round=5, units_sold=-34)
            error_mgs = "there was no error"
        except:
            error_mgs = "error message"
        finally:
            self.assertEqual(error_mgs, "error message")


class TestRoundStatModel(TestCase):

    def test_object_creation_and_name(self):
        market = Market.objects.create(round=5)
        roundstat = RoundStat.objects.create(market=market, round=3, avg_price=34.343) 
        r1 = RoundStat.objects.first()
        self.assertIsInstance(r1, RoundStat)
        self.assertEqual(r1.market, market)
        self.assertEqual(r1.round, 3)
        self.assertEqual(float(r1.avg_price), 34.343)
        self.assertEqual(str(r1), f"{market.market_id}[3]")


    def test_market_and_round_uinque_together(self):
        market1 = Market.objects.create(round=5)
        market2 = Market.objects.create(round=5)
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



           
