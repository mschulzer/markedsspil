from unicodedata import decimal
from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade, filter_trades
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade
from ..forms import TraderForm
from ..helpers import filter_trades

class TwoPlayerGame(TestCase):
     
    def test_round_1_one_forced_moce(self):

        # A teacher creates a market
        post_data = {
            'alpha': 21.402, 
            'beta': 44.2,
            'theta': 2.0105, 
            'min_cost': 11, 
            'max_cost': 144}

        self.client.post(
            reverse('market:create'), 
            post_data
        )
        market = Market.objects.all().first()
        
        # A player named Marianne joins the market:

        self.client.post(
            reverse('market:join'),
            {
                'username': 'Marianne',
                'market_id': market.market_id,
            }
        )

        marianne = Trader.objects.get(name='Marianne')

        # Marianne makes a trade:
        post_data = {
            'unit_price': '10.9', 
            'unit_amount': '45'
            }

        self.client.post(
            reverse(
                'market:play', 
                args=(market.market_id,)), 
                post_data
            )
        
        trade1 = Trade.objects.first()

        # let's assert that the trade was not forced and that the player is ready
        self.assertFalse(trade1.was_forced)
        self.assertTrue(marianne.is_ready())

        # Now a player called Klaus joins the game

        self.client.post(
            reverse('market:join'),
            {
                'username': 'Klaus',
                'market_id': market.market_id,
            }
           
        )

        klaus = Trader.objects.get(name='Klaus')

        # Klaus has not made a trade yet so let's assert that klaus it not ready at this point        
        self.assertFalse(klaus.is_ready())

        
        # Even though Klaus is not ready, the teacher chooses to proceed to the next round:
        url = reverse('market:monitor', args=(market.market_id,))
        self.client.post(url)

        # There should now be 2 trades in the database & Klaus trade should be forced
        self.assertEqual(Trade.objects.all().count(),2)
        klaus_trade=Trade.objects.get(trader=klaus)
        self.assertTrue(klaus_trade.was_forced)

        # Mariannes profit and balance_after should now be set in her trade
        mariannes_trade = Trade.objects.get(trader=marianne)
        self.assertIsNotNone(mariannes_trade.profit)
        self.assertIsNotNone(mariannes_trade.balance_after)

        # Mariannes current balance should be equal to the balance set in her recent trade
        marianne = Trader.objects.get(name='Marianne')
        self.assertEqual(mariannes_trade.balance_after, marianne.balance)

        # we are now in round 1
        market = Market.objects.first()
        self.assertEqual(market.round, 1)

    
    def test_round_1_one_forced_moce(self):

        market = Market.objects.create(round=1)
        marianne = Trader.objects.create(market=market, name="Marianne")
        klaus = Trader.objects.create(market=market, name="Klaus")

        # round zero trades
        m0 = Trade.objects.create(trader=marianne, round=0, unit_price=2, unit_amount=4, profit=30,balance_after=5030, was_forced=False)
        k0 = Trade.objects.create(trader=klaus, round=0,unit_price=None, unit_amount=None, profit=None, balance_after=None, was_forced=True)

        # round 1 trades
        m1= Trade.objects.create(trader=marianne, round=1, unit_price=4,
                             unit_amount=2, profit=None, balance_after=None, was_forced=False)

        # let's assert that the trade was not forced and that the player is ready
        self.assertFalse(m1.was_forced)
        self.assertTrue(marianne.is_ready())
        self.assertFalse(klaus.is_ready())

        # Even though Klaus is not ready, the teacher chooses to proceed to the next round:
        url = reverse('market:monitor', args=(market.market_id,))
        self.client.post(url)

        # Klaus' balance is now set to 5000
        self.assertTrue(klaus.balance==5000)

        # a forced trade has been made for Klaus
        klaus_trade = Trade.objects.get(
            trader=klaus, round=1)   # we are now in round 1
        self.assertTrue(klaus_trade.was_forced)

        # we are now in round 2
        market.refresh_from_db()
        self.assertEqual(market.round, 2)
