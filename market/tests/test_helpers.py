"""
To run all tests:
$ make test

To run all tests in this file:
$ make test_helpers

To run only one or some tests:
docker-compose -f docker-compose.dev.yml run web pytest -k <substring of test function names to run>
"""

from django.test import TestCase
from ..helpers import create_forced_trade, process_trade, generate_balance_list
from decimal import Decimal
from decimal import Decimal
from .factories import MarketFactory, TraderFactory, TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory


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
        trade = TradeFactory(trader=trader, unit_price=Decimal(
            '12234.00'), unit_amount=22)

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


def test_trade_fields_calculated_and_saved_properly(db):
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
    assert expenses == expected_expenses
    assert expected_raw_demand == raw_demand
    assert demand == expected_demand
    assert units_sold == expected_units_sold
    assert income == expected_income
    assert trade_profit == expected_profit

    # test objects updated correctly
    assert trader.balance == Decimal('-5780.00')
    assert trade.profit == Decimal('-5800.00')
    assert trade.balance_after == Decimal('-5780.00')


def test_trade_fields_calculated_and_saved_properly_weird_values(db):
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
    trade = TradeFactory(trader=trader, unit_price=Decimal(
        '12234.00'), unit_amount=22)

    expenses, raw_demand, demand, units_sold, income, trade_profit = process_trade(
        market, trade, avg_price)

    # test calculations
    expected_expenses = Decimal('110.00')
    expected_raw_demand = Decimal('-141146429.820000')
    expected_demand = 0
    expected_units_sold = 0
    expected_income = Decimal('0.00')
    expected_profit = Decimal('-110.00')
    assert expenses == expected_expenses
    assert expected_raw_demand == raw_demand
    assert demand == expected_demand
    assert units_sold == expected_units_sold
    assert income == expected_income
    assert trade_profit == expected_profit

    # test objects updated correctly
    assert trader.balance == Decimal('-230.00')
    assert trade.profit == Decimal('-110.00')
    assert trade.balance_after == Decimal('-230.00')


def test_create_forced_trade_when_trader_not_new(db):
    """ 
    The create_forced_trade function works properly for traders who are not new.
    (This happens when a trader, who has already joined the game, does not make a trade in time in current round)
    """
    trader = TraderFactory()
    # a trader who already has a balance, forgets to trade in round 5. Hence we create a forced trade for this round
    forced_trade = create_forced_trade(
        trader=trader, round_num=5, is_new_trader=False)

    assert forced_trade.was_forced
    assert forced_trade.round == 5
    # traders balance from previous round should carry over
    assert forced_trade.balance_after == trader.balance
    # the balance before the trade should be equal to the traders balance
    assert forced_trade.balance_before == trader.balance
    assert forced_trade.profit is None
    assert forced_trade.unit_price is None
    assert forced_trade.unit_amount is None
    assert forced_trade.units_sold is None
    assert forced_trade.demand is None


def test_create_forced_trade_new_trader(db):
    """ 
    The create_forced_trade function works properly when used to create null trades for previous rounds.
    (this happens when a new trader joins the game late)
    """

    trader = TraderFactory()
    # a trader joins in some round, say round 9, and we create a forced trade for round 5
    forced_trade = create_forced_trade(
        trader=trader, round_num=5, is_new_trader=True)

    assert forced_trade.was_forced
    assert forced_trade.round == 5
    # balance should be None, as trader had yet no balance in this previous round
    assert forced_trade.balance_after is None
    assert forced_trade.balance_before is None
    assert forced_trade.profit is None
    assert forced_trade.unit_price is None
    assert forced_trade.unit_amount is None
    assert forced_trade.units_sold is None
    assert forced_trade.demand is None


class TestGenerateBalanceList(TestCase):

    def test_trader_who_joined_in_round_1_a(self):
        """ 
        The balance list should consist of a list of balances during round 0, 1, 2, etc.
        If a trader joined in round 0, the first element in the list should be the initial balance. 
        """
        market = MarketFactory(round=0)
        trader = TraderFactory(round_joined=0, market=market)

        # There are no trades, so the balance list should at this point only consist of the initial balance of the market (balance in round 0)
        self.assertEqual(generate_balance_list(trader), [
                         float(market.initial_balance)])

        # We create a (processed) trade in round 0 & change that market round to 1
        trade = TradeFactory(trader=trader, round=0,
                             balance_after=Decimal('4500.32'), balance_before=Decimal('5000.0'))
        market.round = 1
        market.save()

        # The balance list should now consist of the initial balance followed by the balance  in 1

        self.assertEqual(generate_balance_list(trader), [
                         float(market.initial_balance), 4500.32])

        # We create a (un-processed) trade in round 1. This should not affect the balance list
        trade = UnProcessedTradeFactory(trader=trader, round=1)
        self.assertEqual(generate_balance_list(trader), [
                         float(market.initial_balance), 4500.32])

    def test_trader_who_joined_in_round_2(self):
        """
        The balance list should consist of a list of balances during round 0, 1, 2, etc.
        If a trader joined in round 2, the list should look like [None, None, initial balance, ... ]
        """
        market = MarketFactory(round=2)
        # A trader joind a market in round 2 and gets the initial balance, say 5000
        trader = TraderFactory(
            round_joined=2, balance=market.initial_balance, market=market)

        # When the trader joins in round 2, forced trades will be produced for round 0 and 1
        ForcedTradeFactory(round=0, trader=trader)
        ForcedTradeFactory(round=1, trader=trader)

        # At this point, the balance list should be [None, None, 5000]
        self.assertEqual(generate_balance_list(trader)[0], None)
        self.assertEqual(generate_balance_list(trader)[1], None)
        self.assertEqual(generate_balance_list(
            trader)[2], market.initial_balance)
        self.assertEqual(len(generate_balance_list(trader)), 3)
