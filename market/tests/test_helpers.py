from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade


class TestCreateForcedTrade(TestCase):

    def setUp(self):
        """ Setup this test data before each test method in clas """
        self.market = Market.objects.create()
        self.trader = Trader.objects.create(market=self.market)
    
    def test_setup_data(self):
        self.assertEqual(self.market.round, 0)
        self.assertEqual(self.trader.market.round, 0)

    def test_market_and_trade_in_round_0(self):
        forced_trade = create_forced_trade(trader=self.trader, round_num=0)
        self.assertIsInstance(forced_trade, Trade)
        self.assertTrue(forced_trade.was_forced)
        self.assertEqual(forced_trade.round, 0)

        trades = Trade.objects.filter(trader=self.trader)
        self.assertEqual(trades.count(), 1)
        self.assertEqual(trades[0].round, 0)
        self.assertEqual(trades[0].profit, None)
        self.assertEqual(trades[0].balance_after, None)

    def test_market_in_round_5_forced_trades_made_in_round_round_0_and_3(self):
        self.market.round = 5
        self.market.save()

        forced_trade = create_forced_trade(trader=self.trader, round_num=0, balance_after=5000, profit=0)
        self.assertEqual(forced_trade.round, 0)
        self.assertEqual(forced_trade.balance_after, 5000)
        self.assertEqual(forced_trade.profit, 0)

        forced_trade = create_forced_trade(trader=self.trader, round_num=3)
        self.assertEqual(forced_trade.round, 3)
        
        forced_trades = Trade.objects.filter(trader=self.trader)
        self.assertEqual(forced_trades.count(), 2)

