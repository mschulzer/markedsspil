"""
To only run tests in this file:
$ docker-compose exec web python manage.py test market.tests.test_forms
"""
# Create your tests here.
from django.test import TestCase
from ..models import Market, Trader, Trade
from ..forms import MarketForm, TraderForm, TradeForm, MarketUpdateForm
from django.core.exceptions import ValidationError
from .factories import MarketFactory, TraderFactory
from decimal import Decimal

class MarketFormTest(TestCase):

    def setUp(self):
        self.data = {
            'product_name_singular':'baguette',
            'product_name_plural':'baguettes',
            'initial_balance':3000, 
            'alpha': 12.1234, 
            'beta': 5.0334,
            'theta': 3.4432, 
            'min_cost': 3, 
            'max_cost': 6,
            'max_rounds': 15,
            'endless': False
        }
        

    def test_market_created(self):
        """ Submitting the market form creates a market."""
        form = MarketForm(data=self.data)
        
        form.is_valid()
        form.save()

        self.assertEqual(Market.objects.filter(min_cost=3).count(), 1)


    def test_alpha_with_5_decimalplaces_is_invalid(self):
        """ alpha, beta and theta can have at most 4 decimalplaces """
        self.data['alpha']= 12.12345
        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)

        self.assertTrue('alpha' in form.errors)
        self.assertTrue('Der må maksimalt være 4 decimaler' in str(form.errors))
        self.assertFalse('beta' in form.errors)


    def test_alpha_with_bigger_than_9999999999_is_invalid(self):
        """ alpha, beta and theta can't be bigger than 9999999999.9999 """
        self.data['alpha']=108880000000000
        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('alpha' in form.errors)
        self.assertFalse('beta' in form.errors)

        self.assertTrue(
            'Der må maksimalt være 14 cifre i alt.' in str(form.errors))

    def test_min_cost_and_max_cost_cant_be_negative(self):
        """ minimal and maximal production cost can't be negative """
        self.data['min_cost'] = -3
        self.data['max_cost'] = -2.34
        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue('max_cost' in form.errors)
        self.assertTrue(
            'Denne værdi skal være større end eller lig 0.01.' in form.errors['min_cost'])
        self.assertTrue(
            'Denne værdi skal være større end eller lig 0.01.' in form.errors['max_cost'])


    def test_min_cost_and_max_cost_cant_be_zero(self):
        """ min cost can't be zero """
        self.data['min_cost'] = 0
        self.data['max_cost'] = 0

        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue('max_cost' in form.errors)
        self.assertTrue(
                    'Denne værdi skal være større end eller lig 0.01.' in form.errors['min_cost'])
        self.assertTrue(
            'Denne værdi skal være større end eller lig 0.01.' in form.errors['max_cost'])

    def test_min_cost_bigger_than_max_cost_is_invalid(self):
        """ min_cost can't be bigger than max_cost """
        self.data['max_cost'] = 2 # min_cost = 3
        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue("Min cost can&#x27;t be bigger than max cost" in str(form))
        self.assertRaises(ValidationError, form.clean)
        self.assertRaises(ValueError, form.save)


    def test_blank_field_is_invalid(self):
        """ host has too fill in all most values when creating a market """
        data = {}
        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('product_name_singular' in form.errors)
        self.assertTrue('product_name_plural' in form.errors)
        self.assertTrue('alpha' in form.errors)
        self.assertTrue('beta' in form.errors)
        self.assertTrue('theta' in form.errors)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue('max_cost' in form.errors)
        self.assertTrue('initial_balance' in form.errors)
        self.assertTrue('max_rounds' in form.errors)

    def test_alpha_negative_is_invalid(self):
        """ alpha can't be negative """
        self.data['alpha'] = -5.4332
        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('alpha' in form.errors)
        self.assertTrue('beta' not in form.errors)
      
    def test_beta_negative_is_invalid(self):
        """ beta can't be negative """
        self.data['beta'] = -3.03244

        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('beta' in form.errors)


    def test_theta_negative_is_invalid(self):
        """ theta can't be negative """
        self.data['theta'] = -1234,

        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('theta' in form.errors)

    def test_max_rounds_cant_be_zero(self):
        """ max_rounds can't less than 1, in particular not 0 """
        self.data['max_rounds'] = 0

        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('max_rounds' in form.errors)

    def test_max_rounds_cant_non_integer(self):
        """ max_rounds has to be an integer """
        self.data['max_rounds'] = 3.54

        form = MarketForm(data=self.data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('max_rounds' in form.errors)


class MarketUpdateFormTest(TestCase):
    def setUp(self):
        self.data = {
            'product_name_singular': 'ost',
            'product_name_plural': 'baguettes',
            'alpha': 12.1234,
            'beta': 5.0334,
            'theta': 3.4432,
            'max_rounds': 15,
            'endless': False,
            'initial_balance': 4500,
            'min_cost': 30,
            'max_cost': 45
        }

    def test_valid_data(self):
        market = MarketFactory(
            endless=True, round=3)
        form = MarketUpdateForm(self.data, instance=market)

        valid = form.is_valid()

        form.save()
        market.refresh_from_db()
        updated_name = market.product_name_singular

        # form data is vald
        self.assertTrue(valid)

        # product name and endless has been updated
        self.assertEqual(market.product_name_singular, 'ost')
        self.assertEqual(market.endless, False)

        # round has not been updataed
        self.assertEqual(market.round, 3)

    def test_if_endless_max_rounds_is_valid(self):
        """ If endless = True, max_rounds can be chosen smaller than current round of the market """
        market = MarketFactory(round=8)

        self.data['endless'] = True
        self.data['max_rounds'] = 5
        form = MarketUpdateForm(self.data, instance=market)
        self.assertTrue(form.is_valid())

    def test_if_not_endless_max_rounds_can_be_invalid_1(self):
        """ If endless = False, max_rounds must be chosen bigger than current round of the market (>market.round) """
        market = MarketFactory(round=8)
        self.data['endless'] = False
        self.data['max_rounds'] = 5
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())

        self.assertTrue(
            "Number of rounds can&#x27;t be smaller than the current round of the market" in str(form))

    def test_if_not_endless_max_rounds_can_be_invalid_2(self):
        """ If endless = False, max_rounds must be chosen bigger than current round of the market (>market.round) """
        market = MarketFactory(round=8)
        self.data['endless'] = False
        self.data['max_rounds'] = 8
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())

        self.assertTrue(
            "Number of rounds can&#x27;t be smaller than the current round of the market" in str(form))

    def test_if_not_endless_max_rounds_can_be_invalid_2(self):
        """ It is okay to choose current round as last round when editing market """
        market = MarketFactory(round=8)
        self.data['endless'] = False
        self.data['max_rounds'] = 9
        form = MarketUpdateForm(self.data, instance=market)
        self.assertTrue(form.is_valid())

    def test_editing_a_market_that_is_game_over_is_invalid_1(self):
        """ Form should not be valid when game is over """
        market = MarketFactory(round=19, max_rounds=19, endless=False)
        self.assertTrue(market.game_over())
        self.data['max_rounds'] = 1000
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())
        self.assertTrue(
            "game is over" in str(form))

    def test_editing_a_market_that_is_game_over_is_invalid_2(self):
        """ Form should not be valid when game is over """
        market = MarketFactory(round=19, max_rounds=19, endless=False)
        self.assertTrue(market.game_over())
        self.data['product_name_singular'] = 'XXX'
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())
        self.assertTrue(
            "game is over" in str(form))

    def test_max_rounds_cant_be_zero(self):
        """ Form is invalied when max_rounds < 1 """
        market = MarketFactory(round=19, max_rounds=19, endless=False)
        self.data['max_rounds'] = 0
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())
        self.assertTrue('max_rounds' in form.errors)

    def test_max_rounds_cant_be_negative(self):
        """ Form is invalied when max_rounds < 1 """
        market = MarketFactory(round=19, max_rounds=19, endless=False)
        self.data['max_rounds'] = -4
        form = MarketUpdateForm(self.data, instance=market)
        self.assertFalse(form.is_valid())
        self.assertTrue('max_rounds' in form.errors)

class TraderFormTest(TestCase):

    def test_trader_created(self):
        """ Trader form validates & trader can be saved after adding additonal data """
        market = MarketFactory()
        
        data = {'name': 'Tommy Junior', 'market_id': market.market_id}

        form = TraderForm(data=data)
        is_valid = form.is_valid()

        trader = form.save(commit=False)
        trader.market = market
        trader.balance = market.initial_balance

        form.save()

        self.assertTrue(is_valid)
        self.assertEqual(Trader.objects.filter(name="Tommy Junior", market=market).count(), 1)

    def test_user_has_to_fill_in_name_and_market_id_when_joining_market(self):
        """ leaving a field blank will make form invalid """
        data = {}

        form = TraderForm(data=data)

        is_valid = form.is_valid()
        
        self.assertFalse(is_valid)
        self.assertTrue('name' in form.errors)
        self.assertTrue('market_id' in form.errors)

    def test_market_does_not_exist_is_invalid(self):
        """ Form is invalid if market with provided ID does not exist """

        data = {'name': 'TestUser', 'market_id': 'VESJYPEF'}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue(
            "There is no market with this ID" in str(form))


    def test_name_has_to_be_unique_on_market(self):
        """ Form is invalid if there is already a trader in the market with the requested name """
        market = MarketFactory()
        TraderFactory(name="grethen", market=market)
        data = {'name': 'grethen', 'market_id': market.market_id}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue(
            "There is already a trader with this name on the requested market. Please select another name" in str(form))
    
    
    def test_name_used_on_another_market_is_no_problem(self):
        """ Form should not be invalid just because there is a trader with the wanted name on another market """
        market1 = MarketFactory()
        market2 = MarketFactory()
        TraderFactory(name="grethen", market=market1)
        data = {'name': 'grethen', 'market_id': market2.market_id}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertTrue(is_valid)


class TradeFormTest(TestCase):

    def setUp(self):
        self.data = {
            'unit_price': 7.40,
            'unit_amount': 140
        }

    def test_valid_post_data_gives_valid_form(self):
        form = TradeForm(data=self.data)
        self.assertTrue(form.is_valid())
 
    def test_valid_form_can_be_used_to_create_and_save_new_trader_to_db(self):
        form = TradeForm(data=self.data)
        trader = TraderFactory()
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = trader.market.round
        new_trade.save()
        self.assertIsInstance(new_trade, Trade)
        self.assertEqual(Trade.objects.all().count(), 1)

    def test_amount_not_integer_gives_invalid_form(self):
        self.data['unit_amount'] = 140.3
        form = TradeForm(data=self.data)
        self.assertFalse(form.is_valid())
     
    def test_init_with_trader_as_argument(self):
        """ 
        trade form is created when a trader is provided as optional argument, and max_amount is calculated properly 
        from traders balance and production cost
        """
        trader = TraderFactory(prod_cost=10, balance=201)
        form = TradeForm(trader, data=self.data)
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = trader.market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)
        self.assertIn('max="20"',str(form)) # balance/prod_cost=20,5 

    def test_form_init__doesnt_crash_when_prod_cost_is_zero(self):
        """ however, production costs should never be allowed to be zero ... """
        trader = TraderFactory(prod_cost=0, balance=201)
        form = TradeForm(trader, data=self.data)
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = trader.market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)
