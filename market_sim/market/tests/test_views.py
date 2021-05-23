# Create your tests here.
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ..models import Market, Trader
from django.core.exceptions import ValidationError
from ..forms import TraderForm


class HomeViewTests(TestCase):

    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/home.html'),

    def test_view_url_exits_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/home.html'),


class CreateMarketViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.valid_data = {'alpha': 21.402, 'beta': 44.2,
                    'theta': 2.0105, 'min_cost': 11, 'max_cost': 144}

        cls.invalid_data = {'alpha': 21.402, 'beta': 44.2,
                          'theta': 2.0105, 'min_cost': 11, 'max_cost': 10}

        cls.invalid_data2 = {'alpha': '', 'beta': 44.2,
                                'theta': 2.0105, 'min_cost': 11, 'max_cost': 10}

    # test get requests
    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    def test_view_url_exits_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    # test post requests
    
    def test_market_is_created_when_data_is_valid(self):
        self.assertEqual(Market.objects.all().count(), 0)
        response = self.client.post(
            reverse('market:create'), self.valid_data)
        self.assertEqual(Market.objects.all().count(), 1)

    def test_redirect_to_corrent_url_after_market_creation(self):
        response = self.client.post(
            reverse('market:create'), self.valid_data)
        self.assertEqual(response.status_code, 302)
        market_id = Market.objects.first().market_id
        self.assertEqual(response['Location'], reverse('market:monitor', args=(market_id,)))

    def test_no_market_is_created_when_min_cost_bigger_than_max_cost_and_error_mgs_is_generated(self):
        response = self.client.post(
            reverse('market:create'), self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Market.objects.all().count(),0)
        html = response.content.decode('utf8')
        self.assertIn("Min cost can&#x27;t be bigger than max cost", html)

    def test_no_market_is_created_when_alpha_not_defined_and_error_mgs_is_generated(self):
        response = self.client.post(
            reverse('market:create'), self.invalid_data2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Market.objects.all().count(), 0)
        html = response.content.decode('utf8')
        self.assertIn("This field is required.", html)
        # other errors that could be tested: alpha has too many digits, min_cost not integer....

class JoinViewTest(TestCase):

    # test get requests

    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/join/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/join.html'),

    def test_view_url_exists_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:join'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/join.html'),

    def test_context_form_when_market_id_is_not_in_GET(self):
        response = self.client.get(reverse('market:join'))
        html = response.content.decode('utf8')
        self.assertNotIn('KXZCVCZL', html)
        self.assertIsInstance(response.context['form'], TraderForm)

    def test_context_form_when_market_id_is_in_GET(self):
        response = self.client.get(reverse('market:join') + "?market_id=KXZCVCZL")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TraderForm)

        html = response.content.decode('utf8')
        self.assertIn('name="market_id" value="KXZCVCZL"', html)

    # test post requests

    def test_proper_behavior_when_no_market_id_in_form(self):
        response = self.client.post(reverse('market:join'), {'username':'Helle', 'market_id':''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)

        html = response.content.decode('utf8')
        self.assertIn('This field is required', html)
        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behavior_when_no_username_in_form(self):
        response = self.client.post(reverse('market:join'), {
                                    'username': '', 'market_id': 'SOME_MARKET_ID'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)

        html = response.content.decode('utf8')
        self.assertIn('<strong>This field is required.</strong>', html)
        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behavior_when_no_market_with_posted_market_id(self):
        market_id_with_no_referent = 'BAD_MARKET_ID'
        response = self.client.post(reverse('market:join'), {
                                    'username': 'Hanne', 'market_id': market_id_with_no_referent})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)
        html = response.content.decode('utf8')
        self.assertIn('<strong>There is no market with this ID</strong>', html)
        self.assertEqual(Trader.objects.all().count(), 0)

    def test_new_trader_created_when_form_is_valid(self):
        market = Market.objects.create()
        response = self.client.post(reverse('market:join'), {
                                    'username': 'Hanne', 'market_id': market.market_id})
        self.assertEqual(Trader.objects.all().count(), 1)
        new_trader = Trader.objects.first()
        self.assertEqual(new_trader.market, market)
        self.assertTrue('trader_id' in self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/{market.market_id}/play/')

        

class MonitorViewTest(TestCase):
 
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        url = f"/{self.market.market_id}/monitor/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/monitor.html'),
    
    def test_view_url_exists_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(
        reverse('market:monitor', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/monitor.html'),

    def test_market_is_in_context(self):
        response = self.client.get(reverse('market:monitor', args=(self.market.market_id,)))
        self.assertEqual(response.context['market'].market_id, self.market.market_id)
        self.assertEqual(response.context['market'].round, 0)
    
    def test_bad_market_id_raises_404(self):
        response = self.client.get(reverse('market:monitor', args=('BAD_MARKET_ID',)))
        self.assertEqual(response.status_code, 404)

    def test_post_method_not_allowed(self):
        response = self.client.post(reverse('market:monitor', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 405)
    
class PlayViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

    def test_market_id_not_found_in_db_returns_404(self):
        response = self.client.get(
            reverse('market:play', args=('BADMARKETID',))
        )
        self.assertEqual(response.status_code, 404)

    
    def test_good_market_id_but_trader_id_not_in_session_redirects_to_join_with_market_id_as_get_param(self):
        # Market exists in database
        # Problem: No 'trader_id' in session
        # Expected behavior: Redirect to 'join'-page with market-id filled out
        response = self.client.get(
            reverse('market:play', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:join') + f'?market_id={self.market.market_id}')

    def test_good_market_id_and_trader_id_in_session_but_user_not_in_db_redirects_to_join_with_market_id_as_get_param(self):
        # Market exists in Market database
        # 'trader_id' is in session
        # Problem: 'trader_id' not found in Trader database
        # Expected behavior: Redirect to 'join'-page with market-id filled out
        session = self.client.session
        session['trader_id'] = 17
        session.save()
        self.assertTrue('trader_id' in self.client.session)
        self.assertEqual(self.client.session['trader_id'], 17)
        response = self.client.get(
            reverse('market:play', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join') + f'?market_id={self.market.market_id}')
    
    def test_good_market_id_and_trader_id_in_session__but_trader_in_wrong_market_returns_redirect_to_join(self):
        # Market exists in Market databate
        # trader_id is in session
        # trader_id has matching entry in Trader database
        # Problem: trader is associated to the wrong market
        # expected behavior: redirect to join with no filled-out values
        other_market = Market.objects.create()
        trader = Trader.objects.create(name='otto', market=other_market)

        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        response = self.client.get(
            reverse('market:play', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_no_errors_views_returns_play_template_and_code_200(self):
        # Market exists in Market databate
        # trader_id is in session
        # trader_id has matching entry in Trader database
        # trader is associated with the correct market
        # expected behavior: return play template
        trader = Trader.objects.create(name='otto', market=self.market)

        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        response = self.client.get(
            reverse('market:play', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),


# to do
class SellViewTest(TestCase):
    pass

class WaitViewTest(TestCase):
    pass

class TraderInMarketViewTest(TestCase):
    pass

class TradersThisRoundViewTest(TestCase):
    pass

class AllTradesViewTest(TestCase):
    pass

class CurrentRoundViewTest(TestCase):
    pass

class DownloadViewTest(TestCase):
    pass
