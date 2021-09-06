"""
To only run the tests in this file:
$ docker-compose run web pytest market/tests/test_forms.py
"""
# Create your tests here.
from django.test import TestCase
from ..models import Market, Trader, Trade
from ..forms import MarketForm, TraderForm, TradeForm, MarketUpdateForm
from django.core.exceptions import ValidationError
from .factories import MarketFactory, TraderFactory

import pytest

from decimal import Decimal


@pytest.fixture
def form_data():
    return {
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
    

def test_market_created(form_data):
    """ Submitting the market form creates a market."""
    form = MarketForm(data=form_data)

    form.is_valid()
    form.save()

    assert (Market.objects.filter(min_cost=3).count() == 1)


def test_alpha_with_5_decimalplaces_is_invalid(form_data):
    """ alpha, beta and theta can have at most 4 decimalplaces """
    form_data['alpha']= 12.12345
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)

    assert ('alpha' in form.errors)
    assert ('Der må maksimalt være 4 decimaler' in str(form.errors))
    assert not ('beta' in form.errors)


def test_alpha_with_bigger_than_9999999999_is_invalid(form_data):
    """ alpha, beta and theta can't be bigger than 9999999999.9999 """
    form_data['alpha']=108880000000000
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('alpha' in form.errors)
    assert not ('beta' in form.errors)

    assert (
        'Der må maksimalt være 14 cifre i alt.' in str(form.errors))

def test_min_cost_and_max_cost_cant_be_negative(form_data):
    """ minimal and maximal production cost can't be negative """
    form_data['min_cost'] = -3
    form_data['max_cost'] = -2.34
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('min_cost' in form.errors)
    assert ('max_cost' in form.errors)
    assert (
        'Denne værdi skal være større end eller lig 0.01.' in form.errors['min_cost'])
    assert (
        'Denne værdi skal være større end eller lig 0.01.' in form.errors['max_cost'])


def test_min_cost_and_max_cost_cant_be_zero(form_data):
    """ min cost can't be zero """
    form_data['min_cost'] = 0
    form_data['max_cost'] = 0

    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('min_cost' in form.errors)
    assert ('max_cost' in form.errors)
    assert (
                'Denne værdi skal være større end eller lig 0.01.' in form.errors['min_cost'])
    assert (
        'Denne værdi skal være større end eller lig 0.01.' in form.errors['max_cost'])

def test_min_cost_bigger_than_max_cost_is_invalid(form_data):
    """ min_cost can't be bigger than max_cost """
    form_data['max_cost'] = 2 # min_cost = 3
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ("Min cost can&#x27;t be bigger than max cost" in str(form))
    with pytest.raises(ValidationError):
        form.clean()
    with pytest.raises(ValueError):
        form.save()

def test_blank_field_is_invalid():
    """ host has too fill in all most values when creating a market """
    data = {}
    form = MarketForm(data=data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('product_name_singular' in form.errors)
    assert ('product_name_plural' in form.errors)
    assert ('alpha' in form.errors)
    assert ('beta' in form.errors)
    assert ('theta' in form.errors)
    assert ('min_cost' in form.errors)
    assert ('max_cost' in form.errors)
    assert ('initial_balance' in form.errors)
    assert ('max_rounds' in form.errors)

def test_alpha_negative_is_invalid(form_data):
    """ alpha can't be negative """
    form_data['alpha'] = -5.4332
    form = MarketForm(data=form_data)


def test_market_created(db, form_data):
    """ Submitting the market form creates a market."""
    form = MarketForm(data=form_data)
    assert form.is_valid()
    form.save()
    assert Market.objects.filter(min_cost=3).count() == 1


def test_alpha_with_5_decimalplaces_is_invalid(form_data):
    """ alpha, beta and theta can have at most 4 decimalplaces """
    form_data['alpha']= 12.12345
    form = MarketForm(data=form_data)

    assert not form.is_valid()
    assert 'alpha' in form.errors
    assert 'Ensure that there are no more than 4 decimal places' in str(form.errors)
    assert not ('beta' in form.errors)



def test_alpha_with_bigger_than_9999999999_is_invalid(form_data):
    """ alpha, beta and theta can't be bigger than 9999999999.9999 """
    form_data['alpha'] = 108880000000000
    form = MarketForm(data = form_data)

    assert not form.is_valid()
    assert 'alpha' in form.errors
    assert not ('beta' in form.errors)
    assert 'Ensure that there are no more than 14 digits in total.' in str(form.errors)

def test_min_cost_and_max_cost_cant_be_negative(form_data):
    """ minimal and maximal production cost can't be negative """
    form_data['min_cost'] = -3
    form_data['max_cost'] = -2.34
    form = MarketForm(data=form_data)

    assert not form.is_valid()

    assert 'min_cost' in form.errors
    assert 'max_cost' in form.errors
    assert 'Ensure this value is greater than or equal to 0.01.' in form.errors['min_cost']
    assert 'Ensure this value is greater than or equal to 0.01.' in form.errors['max_cost']

def test_max_rounds_cant_be_zero(form_data):
    """ max_rounds can't less than 1, in particular not 0 """
    form_data['max_rounds'] = 0
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('max_rounds' in form.errors)

def test_max_rounds_cant_non_integer(form_data):
    """ max_rounds has to be an integer """
    form_data['max_rounds'] = 3.54
    form = MarketForm(data=form_data)

    is_valid = form.is_valid()

    assert not (is_valid)
    assert ('max_rounds' in form.errors)


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


def test_min_cost_and_max_cost_cant_be_zero(form_data):
    """ min cost can't be zero """
    form_data['min_cost'] = 0
    form_data['max_cost'] = 0
    form = MarketForm(data=form_data)

    assert not form.is_valid()
    assert 'min_cost' in form.errors
    assert 'max_cost' in form.errors
    assert 'Ensure this value is greater than or equal to 0.01.' in form.errors['min_cost']
    assert 'Ensure this value is greater than or equal to 0.01.' in form.errors['max_cost']

def test_min_cost_bigger_than_max_cost_is_invalid(form_data):
    """ min_cost can't be bigger than max_cost """
    form_data['max_cost'] = 2 # min_cost = 3
    form = MarketForm(data=form_data)
    assert not form.is_valid()
    assert "Min cost can&#x27;t be bigger than max cost" in str(form)
    with pytest.raises(ValidationError):
        form.clean()
    with pytest.raises(ValueError):
        form.save()


def test_blank_field_is_invalid():
    """ host has too fill in all values when creating a market """
    form = MarketForm(data={})


    assert not form.is_valid()
    assert 'product_name_singular' in form.errors
    assert 'product_name_plural' in form.errors
    assert 'alpha' in form.errors
    assert 'beta' in form.errors
    assert 'theta' in form.errors
    assert 'min_cost' in form.errors
    assert 'max_cost' in form.errors
    assert 'initial_balance' in form.errors

def test_alpha_negative_is_invalid(form_data):
    """ alpha can't be negative """
    form_data['alpha'] = -5.4332
    form = MarketForm(data=form_data)

    assert not form.is_valid()
    assert 'alpha' in form.errors
    assert 'beta' not in form.errors

def test_beta_negative_is_invalid(form_data):
    """ beta can't be negative """
    form_data['beta'] = -3.03244
    form = MarketForm(data=form_data)

    assert not form.is_valid()
    assert 'beta' in form.errors


def test_theta_negative_is_invalid(form_data):
    """ theta can't be negative """
    form_data['theta'] = -1234

    form = MarketForm(data=form_data)
    assert not form.is_valid()
    assert 'theta' in form.errors


def test_trader_created(db):
    """ Trader form validates & trader can be saved after adding additonal data """
    market = MarketFactory()
    data = {'name': 'Tommy Junior', 'market_id': market.market_id}
    form = TraderForm(data=data)
    assert form.is_valid()

    trader = form.save(commit=False)
    trader.market = market
    trader.balance = market.initial_balance

    form.save()

    assert Trader.objects.filter(name="Tommy Junior", market=market).count() == 1

def test_user_has_to_fill_in_name_and_market_id_when_joining_market():
    """ leaving a field blank will make form invalid """
    form = TraderForm(data={})
    assert not form.is_valid()
    assert 'name' in form.errors
    assert 'market_id' in form.errors

def test_market_does_not_exist_is_invalid(db):
    """ Form is invalid if market with provided ID does not exist """
    data = {'name': 'TestUser', 'market_id': 'VESJYPEF'}
    form = TraderForm(data=data)

    assert not form.is_valid()
    assert "There is no market with this ID" in str(form)


def test_name_has_to_be_unique_on_market(db):
    """ Form is invalid if there is already a trader in the market with the requested name """
    market = MarketFactory()
    TraderFactory(name="grethen", market=market)
    data = {'name': 'grethen', 'market_id': market.market_id}
    form = TraderForm(data=data)

    assert not form.is_valid()
    assert "There is already a trader with this name on the requested market. Please select another name" in str(form)


def test_name_used_on_another_market_is_no_problem(db):
    """ Form should not be invalid just because there is a trader with the wanted name on another market """
    market1 = MarketFactory()
    market2 = MarketFactory()
    TraderFactory(name="grethen", market=market1)
    data = {'name': 'grethen', 'market_id': market2.market_id}
    form = TraderForm(data=data)

    assert form.is_valid()


@pytest.fixture
def trader_form_data():
    return {
        'unit_price': 7.40,
        'unit_amount': 140
    }

def test_valid_post_data_gives_valid_form(trader_form_data):
    form = TradeForm(data=trader_form_data)
    assert form.is_valid()

def test_valid_form_can_be_used_to_create_and_save_new_trader_to_db(db, trader_form_data):
    form = TradeForm(data=trader_form_data)
    trader = TraderFactory()
    new_trade = form.save(commit=False)
    new_trade.trader = trader
    new_trade.round = trader.market.round
    new_trade.save()
    assert isinstance (new_trade, Trade)
    assert Trade.objects.all().count() == 1

def test_amount_not_integer_gives_invalid_form(trader_form_data):
    trader_form_data['unit_amount'] = 140.3
    form = TradeForm(data=trader_form_data)
    assert not form.is_valid()

def test_init_with_trader_as_argument(db, trader_form_data):
    """ 
    trade form is created when a trader is provided as optional argument, and max_amount is calculated properly 
    from traders balance and production cost
    """
    trader = TraderFactory(prod_cost=10, balance=201)
    form = TradeForm(trader, data=trader_form_data)
    new_trade = form.save(commit=False)
    new_trade.trader = trader
    new_trade.round = trader.market.round
    new_trade.save()
    assert Trade.objects.all().count() == 1
    assert 'max="20"' in str(form) # balance/prod_cost=20,5 

def test_form_init__doesnt_crash_when_prod_cost_is_zero(db, trader_form_data):
    """ however, production costs should never be allowed to be zero ... """
    trader = TraderFactory(prod_cost=0, balance=201)
    form = TradeForm(trader, data=trader_form_data)
    new_trade = form.save(commit=False)
    new_trade.trader = trader
    new_trade.round = trader.market.round
    new_trade.save()
    assert Trade.objects.all().count() == 1

def test_no_input_is_not_valid(db):
    """ Blank fields invalides form """
    trader = TraderFactory(prod_cost=0, balance=201)
    data = {
        'unit_price': '',
        'unit_amount': ''
    }
    form = TradeForm(trader, data=data)
    assert not (form.is_valid())
    assert ('unit_price' in form.errors)
    assert ('unit_amount' in form.errors)

