"""
To only run tests in this file:
$ docker-compose exec web python manage.py test market.tests.test_forms
"""
# Create your tests here.
from django.test import TestCase
from ..models import Market, Trader, Trade
from ..forms import MarketForm, TraderForm, TradeForm
from django.core.exceptions import ValidationError


class MarketFormTest(TestCase):

    def test_market_created(self):
        """ Submitting the market form creates a market."""
        data = {'product_name_singular':'baguette', 'product_name_plural':'baguettes','initial_balance':3000, 'alpha': 12.1234, 'beta': 5.0334,
                           'theta': 3.4432, 'min_cost': 3, 'max_cost': 6}
        form = MarketForm(data=data)
        
        form.is_valid()
        form.save()

        self.assertEqual(Market.objects.filter(min_cost=3).count(), 1)


    def test_alpha_with_5_decimalplaces_is_invalid(self):
        """ alpha, beta and theta can have at most 4 decimalplaces """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'initial_balance': 3000, 'alpha': 2.12345, 'beta': 5.0334,
                                 'theta': 3.4432, 'min_cost': 3, 'max_cost': 6}
        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)

        self.assertTrue('alpha' in form.errors)
        self.assertTrue('Der må maksimalt være 4 decimaler' in str(form.errors))
        self.assertFalse('beta' in form.errors)


    def test_alpha_with_bigger_than_9999999999_is_invalid(self):
        """ alpha, beta and theta can't be bigger than 9999999999.9999 """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'initial_balance': 3000, 'alpha': 108880000000000, 'beta': 5.0334,
                                 'theta': 3.4432, 'min_cost': 3, 'max_cost': 6}
        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('alpha' in form.errors)
        self.assertFalse('beta' in form.errors)

        self.assertTrue(
            'Der må maksimalt være 14 cifre i alt.' in str(form.errors))



    def test_min_cost_must_be_positive(self):
        """ minimal production cost has to positive """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 3231.200, 'beta': 5.0334,
                'theta': 3.4432, 'min_cost': -3, 'max_cost': 6}
        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue(
            'Denne værdi skal være større end eller lig 1.' in form.errors['min_cost'])

    def test_zero_min_cost_is_invalid(self):
        """ min cost can't be zero """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 3, 'beta': 3, 'theta': 1234,
                'min_cost': 0, 'max_cost': 13}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('min_cost' in form.errors)

    def test_zero_max_cost_is_invalid(self):
        """ max  cost cant be zero """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 3, 'beta': 3, 'theta': 1234,
                'min_cost': 2, 'max_cost': 0}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('max_cost' in form.errors)

    def test_zero_max_cost_and_zero_min_cost_is_invalid(self):
        """ min cost and max cost both zero is also invalid """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 3, 'beta': 3, 'theta': 1234,
                'min_cost': 0, 'max_cost': 0}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue('max_cost' in form.errors)


    def test_min_cost_bigger_than_max_cost_is_invalid(self):
        """ min_cost can't be bigger than max_cost """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 3231.200, 'beta': 5.0334,
                'theta': 3.4432, 'min_cost': 3, 'max_cost': 2}
        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)

        self.assertTrue("Min cost can&#x27;t be bigger than max cost" in str(form))
        self.assertRaises(ValidationError, form.clean)
        self.assertRaises(ValueError, form.save)


    def test_blank_field_is_invalid(self):
        """ host has too fill in all values when creating a market """
        data = {}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('product_name_singular' in form.errors)
        self.assertTrue('alpha' in form.errors)
        self.assertTrue('beta' in form.errors)
        self.assertTrue('theta' in form.errors)
        self.assertTrue('min_cost' in form.errors)
        self.assertTrue('max_cost' in form.errors)
        self.assertTrue('initial_balance' in form.errors)

    def test_alpha_negative_is_invalid(self):
        """ alpha can't be negative """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': -3, 'beta': 0, 'theta': 3.2,
                'min_cost': 3, 'max_cost': 13}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('alpha' in form.errors)
        self.assertTrue('beta' not in form.errors)
      
    def test_beta_negative_is_invalid(self):
        """ beta can't be negative """
        data = {'product_name_singular':'baguette', 'product_name_plural':'baguettes', 'alpha': 3, 'beta': -0.13, 'theta': 3.21, 'min_cost':3, 'max_cost':13}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('beta' in form.errors)


    def test_theta_negative_is_invalid(self):
        """ theta can't be negative """
        data = {'product_name_singular': 'baguette', 'product_name_plural': 'baguettes', 'alpha': 0, 'beta': 3, 'theta': -1234,
                'min_cost': 3, 'max_cost': 13}

        form = MarketForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue('theta' in form.errors)



class TraderFormTest(TestCase):

    def test_trader_created(self):
        """ Submitting the trader form and adding a market creates a trader."""
        market = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                       theta=2.0105, min_cost=11, max_cost=144, round=3)
        data = {'name': 'Tommy Junior', 'market_id': market.market_id}

        form = TraderForm(data=data)
        trader = form.save(commit=False)
        trader.market = market
        trader.balance = market.initial_balance

        form.save()

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
        """ Form is invalid if market does not exist """

        data = {'name': 'TestUser', 'market_id': 'VESJYPEF'}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue(
            "There is no market with this ID" in str(form))


    def test_username_is_taken_is_invalid(self):
        """ Form is invalid if there is already a trader in the market with the requested name """
        market = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                       theta=2.0105, min_cost=11, max_cost=144, round=3)
        Trader.objects.create(name="grethen", market=market, balance=market.initial_balance)
        data = {'name': 'grethen', 'market_id': market.market_id}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertTrue(
            "There is already a trader with this name on the requested market. Please select another name" in str(form))
    
    
    def test_username_taken_on_another_name_is_no_problem(self):
        """ Form should not be invalid just because there is a user with the wanted name on another market """
        market1 = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                                 theta=2.0105, min_cost=11, max_cost=144)
        market2 = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                                 theta=2.0105, min_cost=11, max_cost=144, round=3)
        Trader.objects.create(name="grethen", market=market2, balance=market2.initial_balance)
        data = {'name': 'grethen', 'market_id': market1.market_id}
        form = TraderForm(data=data)

        is_valid = form.is_valid()

        self.assertTrue(is_valid)


class TradeFormTest(TestCase):

    def test_valid_post_data_gives_valid_form(self):
        data = {'unit_price': 7, 'unit_amount': 140}
        form = TradeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_amount_not_integer_gives_invalid_form(self):
        data = {'unit_price': 7.3, 'unit_amount': 140.3}
        form = TradeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_valid_form_with_post_data_can_be_saved_to_new_market(self):
        data = {'unit_price': 7, 'unit_amount': 140}
        form = TradeForm(data=data)
        new_trade = form.save(commit=False)
        self.assertIsInstance(new_trade, Trade)

    def test_valid_form_with_all_data_can_be_saved_to_new_market(self):
        data = {'unit_price': 7, 'unit_amount': 140}
        form = TradeForm(data=data)
        new_trade = form.save(commit=False)
        self.assertIsInstance(new_trade, Trade)
        self.assertEqual(Trade.objects.all().count(), 0)

    def test_valid_form_with_all_data_can_be_saved_to_db(self):
        data = {'unit_price': 18, 'unit_amount': 140}
        form = TradeForm(data=data)
        market = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                       theta=2.0105, min_cost=11, max_cost=144, round=3)
        trader = Trader.objects.create(market=market, name="joe", balance=400)
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertIsInstance(new_trade, Trade)
        self.assertEqual(Trade.objects.all().count(), 1)

    def test_init_with_trader_as_argument(self):
        """ trade form is created when trader is argument, and max_amount is calculated properly """
        market = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                       theta=2.0105, min_cost=11, max_cost=144, round=0)
        trader = Trader.objects.create(market=market, name="Hans Lange", prod_cost=10, balance=201)
        data = {'unit_price': 18, 'unit_amount': 140}
        form = TradeForm(trader, data=data)
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)
        self.assertIn('max="20"',str(form)) # balance/prod_price=20,5 

    def test_form_init__doesnt_crash_when_prod_cost_is_zero(self):
        market = Market.objects.create(initial_balance=5000, alpha=21.402, beta=44.2,
                                       theta=2.0105, min_cost=11, max_cost=144, round=0)
        trader = Trader.objects.create(market=market, name="Hans Lange", prod_cost=0, balance=201)
        data = {'unit_price': 18, 'unit_amount': 140}
        form = TradeForm(trader, data=data)
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)
