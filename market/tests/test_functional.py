from django.test import TestCase
from ..models import Market, Trader, Trade
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade
from .factories import TraderFactory, UserFactory, MarketFactory, TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory

# Run tests with english language settings
from django.utils.translation import activate
activate("en-US")

class TwoPlayerGame(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')


    def test_round_0_one_forced_move(self):

        # A teacher creates a market
        post_data = {
            'product_name_singular':'baguette',
            'product_name_plural': 'baguettes',
            'initial_balance':4000,
            'alpha': 21.402, 
            'beta': 44.2,
            'theta': 2.0105, 
            'min_cost': 11, 
            'max_cost': 144,
            'max_rounds': 15,
            'endless': False}
        self.client.post(
            reverse('market:create'), 
            post_data
        )
        self.assertEqual(Market.objects.all().count(),1)

        market = Market.objects.all().first()

        self.assertEqual(market.created_by, self.user)

        # A player named Marianne joins the market:
        self.client.post(
            reverse('market:join'),
            {
                'name': 'Marianne',
                'market_id': market.market_id,
            }
        )
        self.assertEqual(Trader.objects.all().count(), 1)


        marianne = Trader.objects.get(name='Marianne')

        # Marianne makes a trade:
        post_data = {
            'unit_price': '10.9', 
            'unit_amount': '45'
            }

        self.client.post(
            reverse(
                'market:play'), 
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
                'name': 'Klaus',
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

    
    def test_round_1_one_forced_move(self):
        """ Established the state obtained at the end of the test above. Proceeds to test round 1 behaviour """

        market = MarketFactory(round=1, created_by=self.user)
        marianne = TraderFactory(market=market, name="Marianne")
        klaus = TraderFactory(market=market, name="Klaus", balance=324)

        # Historical round zero trades
        m0 = TradeFactory(trader=marianne, round=0)
        k0 = ForcedTradeFactory(trader=klaus, round=0)

        # Marianne makes a trade decision in round 1 (it is not processed yet, so most field should be None)
        m1= UnProcessedTradeFactory(trader=marianne, round=1)
        self.assertTrue(m1.profit is None)

        # Mariannes trade was not forced. Marianne is ready, but Klaus is not
        self.assertFalse(m1.was_forced)
        self.assertTrue(marianne.is_ready())
        self.assertFalse(klaus.is_ready())

        # Even though Klaus is not ready, the teacher chooses to proceed to the next round:
        url = reverse('market:monitor', args=(market.market_id,))
        self.client.post(url)

        # Klaus' balance has not changed
        self.assertEqual(klaus.balance,324)

        # a forced trade has been made for Klaus
        klaus_trade = Trade.objects.get(
            trader=klaus, round=1)   # we are now in round 1
        self.assertTrue(klaus_trade.was_forced)

        # mariannes trade has been processed, so the profit has been calculated
        m1.refresh_from_db()
        self.assertFalse(m1.profit is None)        

        # we are now in round 2
        market.refresh_from_db()
        self.assertEqual(market.round, 2)
