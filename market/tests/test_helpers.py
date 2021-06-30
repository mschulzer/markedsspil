"""
To run only this test suite:
docker-compose exec web python manage.py test market.tests.test_helpers 
"""
from django.test import TestCase
from ..helpers import create_forced_trade, filter_trades, process_trade
from decimal import Decimal
from decimal import Decimal 
from .factories import MarketFactory, TraderFactory, TradeFactory, ForcedTradeFactory

class TestProcessTrade(TestCase):

    def test_trade_fields_calculated_and_saved_properly(self):
        market = MarketFactory(
            alpha=Decimal('100.3000'), 
            beta=Decimal('3.4000'), 
            theta=Decimal('4.5000')
        )
        trader = TraderFactory(
            market=market, 
            balance=Decimal('20.00'), 
            prod_cost=Decimal('70.00')
        )
        avg_price = Decimal('14.50')
        trade = TradeFactory(
            trader=trader, 
            unit_price=Decimal('12.00'), 
            unit_amount=100
        )
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

        # test objects updated correctly
        self.assertEqual(trader.balance, Decimal('-5780.00'))
        self.assertEqual(trade.profit, Decimal('-5800.00'))
        self.assertEqual(trade.balance_after, Decimal('-5780.00'))

    def test_trade_fields_calculated_and_saved_properly_weird_values(self):
        """
        trade values are being calculated correctly in a case where the raw demand is negative
        """
        market = MarketFactory(
            initial_balance=Decimal('40.00'), 
            alpha=Decimal('0.000'),
            beta=Decimal('23233.4000'),
            theta=Decimal('999.0000'),
            min_cost=Decimal('2.00'),
            max_cost=Decimal('10.00')
        )
        trader = TraderFactory(
            market=market, 
            balance=Decimal('-120.00'), 
            prod_cost=Decimal('5.00')
        )
        avg_price = Decimal('143234.22')
        trade = TradeFactory(trader=trader, unit_price=Decimal('12234.00'), unit_amount=22)

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

        # test objects updated correctly
        self.assertEqual(trader.balance, Decimal('-230.00'))
        self.assertEqual(trade.profit, Decimal('-110.00'))
        self.assertEqual(trade.balance_after, Decimal('-230.00'))
        


class TestCreateForcedTrade(TestCase):

    def test_create_forced_trade_when_trader_not_new(self):
        """ 
        The create_forced_trade function works properly for traders who are not new.
        (This happens when a trader, who has already joined the game, does not make a trade in time in current round)
        """
        trader = TraderFactory()
        forced_trade = create_forced_trade(trader=trader, round_num=5, is_new_trader=False)

        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 5)
        self.assertEqual(forced_trade.balance_after, trader.balance) # traders balance from previous round should carry over
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)
        self.assertEqual(forced_trade.units_sold, None)
        self.assertEqual(forced_trade.demand, None)


    def test_create_forced_trade_new_trader(self):
        """ 
        The create_forced_trade function works properly when used to create null trades for previous rounds.
        (this happens when a new trader joins the game late)
        """

        trader = TraderFactory()
        forced_trade = create_forced_trade(trader=trader, round_num=5, is_new_trader=True)

        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 5)
        self.assertEqual(forced_trade.balance_after, None) # balance should be None, as trader had yet no balance in this previous round
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)
        self.assertEqual(forced_trade.units_sold, None)
        self.assertEqual(forced_trade.demand, None)

class TestFilterTrades(TestCase):

    def setUp(self):

        self.market1 = MarketFactory()
        self.trader11 = TraderFactory(market=self.market1)
        self.trader12 = TraderFactory(market=self.market1)
        self.trade1 = TradeFactory(trader=self.trader11, round=0)
        self.trade2 = TradeFactory(trader=self.trader12, round=1)

        self.market2 = MarketFactory()
        self.trader21 = TraderFactory(market=self.market2)
        self.trader22 = TraderFactory(market=self.market2)
        self.trade3 = TradeFactory(trader=self.trader21, round=0)
        self.trade4 = TradeFactory(trader=self.trader22, round=1)

    def test_filter_trades_of_market_two_trades(self):
        """ filter_trades function correctly filters the two two trades associated to (resp.) market 1 and market 2. """

        trades1 = filter_trades(market=self.market1)
        self.assertEqual(trades1.count(),2)
        self.assertEqual(trades1[0], self.trade1)
        self.assertEqual(trades1[1], self.trade2)

        trades2 = filter_trades(market=self.market2)
        self.assertEqual(trades2.count(), 2)
        self.assertEqual(trades2[0], self.trade3)
        self.assertEqual(trades2[1], self.trade4)
    
    def test_filter_trades_of_market_and_round(self):
        """ filter_trades function filters correctly when round number is given """
        trades1 = filter_trades(market=self.market1, round=0)
        self.assertEqual(trades1.count(),1)
        self.assertEqual(trades1[0], self.trade1)

        trades1 = filter_trades(market=self.market1, round=1)
        self.assertEqual(trades1.count(), 1)
        self.assertEqual(trades1[0], self.trade2)

        trades1 = filter_trades(market=self.market1, round=3)
        self.assertEqual(trades1.count(), 0)
