from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade, filter_trades, process_trade
from decimal import Decimal
from math import floor
from decimal import Decimal 

class TestProcessTrade(TestCase):

    def test_trade_fields_calculated_and_saved_properly(self):
        market = Market.objects.create(initial_balance=20, alpha=100.3, beta=3.4, theta=4.5, min_cost=1.00, max_cost=4.00)
        market.refresh_from_db()
        alpha, beta, theta = market.alpha, market.beta, market.theta

        trader = Trader.objects.create(market=market, balance=20.00, prod_cost=70.00)
        trader.refresh_from_db()
        avg_price = Decimal('14.50')
        trade = Trade.objects.create(
             trader=trader, round=0, unit_price=12, unit_amount=100)
        trade.refresh_from_db()
        expenses, raw_demand, demand, units_sold, income, trade_profit = process_trade(
             market, trade, avg_price)

        # test calculations
        expected_expenses = Decimal('7000.00') 
        expected_raw_demand = 124.75  
        expected_demand = 125  
        expected_units_sold = 100.00  
        expected_income = Decimal('1200.00')
        expected_profit = Decimal('-5800.00')
        self.assertEqual(expenses, expected_expenses)
        self.assertEqual(expected_raw_demand, raw_demand)
        self.assertEqual(demand, expected_demand)
        self.assertEqual(units_sold, expected_units_sold)
        self.assertEqual(income, expected_income)
        self.assertEqual(trade_profit, expected_profit)

        # # test object updates
        trader.refresh_from_db()
        trade.refresh_from_db()

        self.assertEqual(trader.balance, Decimal('-5780.00'))
        self.assertEqual(trade.profit, Decimal('-5800.00'))
        self.assertEqual(trade.balance_after, Decimal('-5780.00'))

    def test_trade_fields_calculated_and_saved_properly_weird_values(self):
        """
        trade values are being calculated correctly in a case, where the raw demand is negative
        """
        market = Market.objects.create(initial_balance=40.00, alpha=0, beta=23233.4, theta=999, min_cost=2.00, max_cost=10.00)
        alpha, beta, theta = market.alpha, market.beta, market.theta
        market.refresh_from_db()

        trader = Trader.objects.create(market=market, balance=-120, prod_cost=5)
        trader.refresh_from_db()
        avg_price = Decimal('143234.22')
        trade = Trade.objects.create(
            trader=trader, round=0, unit_price=12234.00, unit_amount=22)
        trade.refresh_from_db()
        expenses, raw_demand, demand, units_sold, income, trade_profit = process_trade(
            market, trade, avg_price)
        
        # test calculations
        expected_expenses = Decimal('110.00') 
        expected_raw_demand = Decimal('-141146429.820000')
        expected_demand = 0  
        expected_units_sold = 0 
        expected_income = Decimal('0.00') 
        expected_profit = Decimal('-110.00')
        self.assertEqual(expenses, expected_expenses)
        self.assertEqual(expected_raw_demand, raw_demand)
        self.assertEqual(demand, expected_demand)
        self.assertEqual(units_sold, expected_units_sold)
        self.assertEqual(income, expected_income)
        self.assertEqual(trade_profit, expected_profit)

        # # test object updates
        trader.refresh_from_db()
        trade.refresh_from_db()
        self.assertEqual(trader.balance, Decimal('-230.00'))
        self.assertEqual(trade.profit, Decimal('-110.00'))
        self.assertEqual(trade.balance_after, Decimal('-230.00'))
        


class TestCreateForcedTrade(TestCase):

    def test_create_forced_trade_NOT_new_trader(self):

        market = Market.objects.create(
            initial_balance=20, alpha=100.3, beta=3.4, theta=4.5, min_cost=1, max_cost=4, round=5)
        trader = Trader.objects.create(market=market, balance=3)
        forced_trade = create_forced_trade(trader=trader, round_num=5, is_new_trader=False)

        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 5)
        self.assertEqual(forced_trade.balance_after, trader.balance) # balance from previous round should carry over
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)

    def test_create_forced_trade_new_trader(self):

        market = Market.objects.create(
            initial_balance=20, alpha=100.3, beta=3.4, theta=4.5, min_cost=1, max_cost=4, round=5)
        trader = Trader.objects.create(market=market, balance=400)
        forced_trade = create_forced_trade(trader=trader, round_num=3, is_new_trader=True)

        # we create a forced trade for an earlier round (when the trader was not yet in the market)
        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 3)
        self.assertEqual(forced_trade.balance_after, None) # balance should be set to zero as trader is new
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)


class TestGetTrades(TestCase):

    def setUp(self):
        """ Setup this test data before each test method in clas """

        self.market1 = Market.objects.create(
            initial_balance=20, alpha=100.3, beta=3.4, theta=4.5, min_cost=1, max_cost=4)

        self.trader11 = Trader.objects.create(market=self.market1, name="trader11", balance=4)
        self.trader12 = Trader.objects.create(market=self.market1, name="trader12", balance=3)
        self.trade1 = Trade.objects.create(trader=self.trader11, round=0)
        self.trade2 = Trade.objects.create(trader=self.trader12, round=1)

        self.market2 = Market.objects.create(
            initial_balance=20, alpha=100.3, beta=3.4, theta=4.5, min_cost=1, max_cost=4)

        self.trader21 = Trader.objects.create(
            market=self.market2, name="trader21", balance=2)
        self.trader22 = Trader.objects.create(market=self.market2, name="trader22", balance=2)
        self.trade3 = Trade.objects.create(trader=self.trader21, round=0)
        self.trade4 = Trade.objects.create(trader=self.trader22, round=1)

    def test_filter_trades_of_market_two_trades(self):
        trades1 = filter_trades(market=self.market1)
        self.assertEqual(trades1.count(),2)
        self.assertEqual(trades1[0], self.trade1)
        self.assertEqual(trades1[1], self.trade2)

        trades2 = filter_trades(market=self.market2)
        self.assertEqual(trades2.count(), 2)
        self.assertEqual(trades2[0], self.trade3)
        self.assertEqual(trades2[1], self.trade4)
    
    def test_filter_trades_of_market_and_round(self):
        trades1 = filter_trades(market=self.market1, round=0)
        self.assertEqual(trades1.count(),1)
        self.assertEqual(trades1[0], self.trade1)

        trades1 = filter_trades(market=self.market1, round=1)
        self.assertEqual(trades1.count(), 1)
        self.assertEqual(trades1[0], self.trade2)

        trades1 = filter_trades(market=self.market1, round=3)
        self.assertEqual(trades1.count(), 0)
