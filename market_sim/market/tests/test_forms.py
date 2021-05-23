# Create your tests here.
from django.test import SimpleTestCase, TestCase
from ..models import Market,Trader
from ..forms import MarketForm, TraderForm
from django.core.exceptions import ValidationError


class TestMarketForm(TestCase):

    def setUp(self):
        # Do this setup before running all test methods in class
        self.valid_data = {'alpha': 2, 'beta': 5.0334,
                                 'theta': 3.4432, 'min_cost': 3, 'max_cost': 6}
        self.valid_form = MarketForm(data=self.valid_data)

    def test_valid_data_gives_valid_form(self):
        self.assertTrue(self.valid_form.is_valid())

    def test_valid_form_can_be_saved(self):
        self.assertEqual(Market.objects.all().count(), 0)
        self.valid_form.save()
        self.assertEqual(Market.objects.all().count(), 1)
        market = Market.objects.first()
        self.assertEqual(market.alpha, 2.0000)
        self.assertEqual(float(market.beta), 5.0334)
        self.assertEqual(float(market.theta), 3.4432)
        self.assertEqual(market.min_cost, 3)
        self.assertEqual(market.max_cost, 6)

    def test_5_decimalplaces_gives_invalid_form_that_cant_be_saved(self):
        invalid_data = self.valid_data
        invalid_data['alpha'] = 2.12345
        form = MarketForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValueError, form.save)

    def test_non_integer_min_cost_gives_invalid_form_that_cant_be_saved(self):
        invalid_data = self.valid_data
        invalid_data['min_cost'] = 2.1
        form = MarketForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValueError, form.save)

    def test_min_cost_bigger_than_max_cost_gives_invalid_form(self):
        invalid_data = self.valid_data
        invalid_data['min_cost'] = self.valid_data['max_cost'] + 1
        form = MarketForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean)
        self.assertRaises(ValueError, form.save)


class TestTraderForm(TestCase):

    def test_valid_data_gives_valid_form(self):
        market = Market.objects.create()
        data = {'username': 'TestUser', 'market_id': market.market_id}
        form = TraderForm(data=data)
        self.assertTrue(form.is_valid())
       
    def test_form_invalid_if_no_market_with_given_id(self):
        data = {'username': 'TestUser', 'market_id': 'VESJYPEF'}
        form = TraderForm(data=data)
        self.assertFalse(form.is_valid())

# to do
class SellFormTest(TestCase):
    pass



