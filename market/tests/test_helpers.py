from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade


class TestCreateForcedTrade(TestCase):

    def setUp(self):
        """ Setup this test data before each test method in clas """
    
    def test_market_in_round_5_forced_trades_made_in_round_3(self):

        # a game is in round 5
        market = Market.objects.create(round=5)
        
        # there is a trader in the market - he has same round
        trader = Trader.objects.create(market=market)

        # a forced trade is made in round 3
        forced_trade = create_forced_trade(trader=trader, round_num=3)

        # the forced trade has been made with correct values
        self.assertEqual(forced_trade.was_forced, True)
        self.assertEqual(forced_trade.round, 3)
        self.assertEqual(forced_trade.balance_after, None)
        self.assertEqual(forced_trade.profit, None)
        self.assertEqual(forced_trade.unit_price, None)
        self.assertEqual(forced_trade.unit_amount, None)


