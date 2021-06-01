from unicodedata import decimal
from django.test import TestCase
from ..models import Market, Trader, Trade
from ..helpers import create_forced_trade, get_trades
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade
from ..forms import TraderForm
from ..views import validate_market_and_trader
from ..helpers import get_trades

class OnePlayerGame(TestCase):
     
    def test_one_player_(self):

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

        post_data = {
            'username': 'Marianne',
            'market_id': market.market_id,
        }

        self.client.post(
            reverse('market:join'),
            post_data
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

        post_data = {
            'username': 'Klaus',
            'market_id': market.market_id,
        }

        self.client.post(
            reverse('market:join'),
            post_data
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
        self.assertEqual(mariannes_trade.balance_after, marianne.balance)