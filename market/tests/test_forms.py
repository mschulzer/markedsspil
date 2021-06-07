# Create your tests here.
from django.test import SimpleTestCase, TestCase
from ..models import Market, Trader, Trade
from ..forms import MarketForm, TraderForm, TradeForm
from django.core.exceptions import ValidationError


class MarketFormTest(TestCase):

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


class TraderFormTest(TestCase):

    def test_form_is_valid_if_market_exists_and_username_not_taken(self):
        market = Market.objects.create()
        data = {'name': 'TestUser', 'market_id': market.market_id}
        form = TraderForm(data=data)
        self.assertTrue(form.is_valid())
       
    def test_form_invalid_if_username_available_but_no_market_with_given_id(self):
        data = {'name': 'TestUser', 'market_id': 'VESJYPEF'}
        form = TraderForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_if_market_exits_but_username_is_taken_by_a_trader_on_this_marker(self):
        market = Market.objects.create()
        Trader.objects.create(name="grethen", market=market)
        data = {'name': 'grethen', 'market_id': market.market_id}
        form = TraderForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_form_valid_if_market_exists_and__username_is_taken_by_a_trader_on_ANOTHER_market(self):
        market1 = Market.objects.create()
        market2 = Market.objects.create()
        Trader.objects.create(name="grethen", market=market2)
        market1.refresh_from_db()
        data = {'name': 'grethen', 'market_id': market1.market_id}
        form = TraderForm(data=data)
        self.assertTrue(form.is_valid())


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
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name="joe")
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertIsInstance(new_trade, Trade)
        self.assertEqual(Trade.objects.all().count(), 1)

    def test_init_with_trader_as_argument(self):
        """ trade form is created when trader is argument, and max_amount is calculated properly """
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name="Hans Lange", prod_cost=10, balance=201)
        data = {'unit_price': 18, 'unit_amount': 140}
        form = TradeForm(trader, data=data)
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name="joe")
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)
        self.assertIn('max="20"',str(form)) # balance/prod_price=20,5 

    def test_form_init__doesnt_crash_when_prod_cost_is_zero(self):
        """ trade form is created when trader is argument, and max_amount is calculated properly """
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name="Hans Lange", prod_cost=0, balance=201)
        data = {'unit_price': 18, 'unit_amount': 140}
        form = TradeForm(trader, data=data)
        market = Market.objects.create()
        trader = Trader.objects.create(market=market, name="joe")
        new_trade = form.save(commit=False)
        new_trade.trader = trader
        new_trade.round = market.round
        new_trade.save()
        self.assertEqual(Trade.objects.all().count(), 1)