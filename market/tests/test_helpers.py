from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade, filter_trades


class TestCreateForcedTrade(TestCase):

    
    def test_create_forced_trade_NOT_new_trader(self):

        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market)
        forced_trade = create_forced_trade(trader=trader, round_num=5, is_new_trader=False)

        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 5)
        self.assertEqual(forced_trade.balance_after, trader.balance) # balance from previous round should carry over
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)

    def test_create_forced_trade_new_trader(self):
        market = Market.objects.create(round=5)
        trader = Trader.objects.create(market=market)
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

        self.market1 = Market.objects.create()
        self.trader11 = Trader.objects.create(market=self.market1, name="trader11")
        self.trader12 = Trader.objects.create(market=self.market1, name="trader12")
        self.trade1 = Trade.objects.create(trader=self.trader11, round=0)
        self.trade2 = Trade.objects.create(trader=self.trader12, round=1)


        self.market2 = Market.objects.create()
        self.trader21 = Trader.objects.create(market=self.market2, name="trader21")
        self.trader22 = Trader.objects.create(market=self.market2, name="trader22")
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
