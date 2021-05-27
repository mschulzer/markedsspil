# Create your tests here.
from django.http import JsonResponse
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade, Stats
from ..forms import TraderForm
from ..views import validate_market_and_trader

class HomeViewTests(TestCase):

    def test_post_requests_not_allowed(self):
        url = reverse('market:home')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
    
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
        self.client.post(
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
        self.assertEqual(response['Location'], reverse('market:play', args=(market.market_id,)))
        
class MonitorViewTest(TestCase):
 
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

    def test_post_requests_not_allowed(self):
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

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


class ValidateMarketAndTrader(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

    def test_market_not_in_db_redirects_to_join(self):
        validation = validate_market_and_trader(self.client.session, 'BADMARKETID')
        self.assertTrue('error_redirect' in validation)
        response = validation['error_redirect']
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_market_in_db_but_trader_id_not_in_session_redirects_to_join_with_market_id_as_get_param(self):
        # Market exists in database
        # Problem: No 'trader_id' in session
        # Expected behavior: Redirect to 'join'-page with market-id filled out
        validation = validate_market_and_trader(
            self.client.session, self.market.market_id)
        self.assertTrue('error_redirect' in validation)
        response = validation['error_redirect']
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

        validation = validate_market_and_trader(session, self.market.market_id)
        self.assertTrue('error_redirect' in validation)
        response = validation['error_redirect']
        self.assertEqual(response['Location'], reverse('market:join') + f'?market_id={self.market.market_id}')

    def test_good_market_id_and_trader_id_in_session_but_trader_in_wrong_market_returns_redirect_to_join(self):
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

        validation = validate_market_and_trader(
            session, self.market.market_id)
        self.assertTrue('error_redirect' in validation)
        response = validation['error_redirect']
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_no_errors_views_returns_context_with_market_and_tracer(self):
        # Market exists in Market databate
        # trader_id is in session
        # trader_id has matching entry in Trader database
        # trader is associated with the correct market
        # expected behavior: return play template
        trader = Trader.objects.create(name='otto', market=self.market)

        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        context = validate_market_and_trader(session, self.market.market_id)
        self.assertIsInstance(context, dict)
        self.assertTrue('market' in context)
        self.assertTrue('trader' in context)
        self.assertEqual(context['trader'], trader)
        self.assertEqual(context['market'], self.market)

"""      
def play(request, market_id):

    validation = validate_market_and_trader(request.session, market_id)
    
    if 'error_redirect' in validation:
        return validation['error_redirect']
 
    market = validation['market']
    trader = validation['trader']

    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            new_trade = form.save(commit=False)
            new_trade.market = market
            new_trade.trader = trader
            new_trade.round = market.round
            new_trade.save()
            return HttpResponseRedirect(reverse('market:wait', args=(market.market_id,)))

        return render(request, 'market/play.html', {'form': form})

    elif request.method == 'GET':
        form = TradeForm()
    
    return render(request, 'market/play.html', {'market':market, 'trader':trader, 'form':form})
"""
class PlayViewTest(TestCase):
    # note: most of the below tests are not really necessary, as the same stuff is being tested in ErrorTrackerTestst

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader_on_market = Trader.objects.create(
                        market=cls.market, name="TraderOnMarket")
    
    ######## test get requests ##########

    def test_get_market_id_not_found_redirects_to_join(self):
        response = self.client.get(
            reverse('market:play', args=('BADMARKETID',))
        )
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

        
    ######## test post requests ##########

    def test_post_market_id_not_found_redirects_to_join(self):

        response = self.client.post(
            reverse('market:play', args=('BADMARKETID',))
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))
  
    def test_if_all_data_is_good_then_save_trade_and_redirect_to_play(self):
        session = self.client.session
        session['trader_id'] = self.trader_on_market.pk
        session.save()
        self.assertEqual(Trade.objects.all().count(), 0)
        response = self.client.post(
            reverse('market:play', args=(self.market.market_id,)), {'unit_price': '10.9', 'unit_amount': '45'})
        self.assertEqual(Trade.objects.all().count(), 1)
        trade = Trade.objects.first()
        self.assertEqual(float(trade.unit_price), 10.9)
        self.assertEqual(trade.unit_amount, 45)
        self.assertEqual(trade.market, self.market)
        self.assertEqual(trade.trader, self.trader_on_market)
        self.assertEqual(trade.round, 0)
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('market:wait', args=(self.market.market_id,))
        self.assertEqual(response['Location'], expected_redirect_url)

class WaitViewTest(TestCase):
    # note: tests in this class are identical to play tests 

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

    def test_post_requests_not_allowed(self):
        url = reverse('market:wait', args=(self.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_market_id_not_found_redirects_to_join(self):

        response = self.client.get(
            reverse('market:wait', args=('BADMARKETID',))
        )
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
            reverse('market:wait', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/wait.html'),

class TraderInMarketViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader = Trader.objects.create(market=cls.market, name="trader_name")
        
        cls.other_market = Market.objects.create()
        cls.other_trader = Trader.objects.create(market=cls.other_market, name="other_trader_name")
        
        cls.empty_market = Market.objects.create()

    def test_response_status_code_200_when_market_exists(self):
        response = self.client.get(
            reverse('market:traders_in_market', args=(self.market.market_id,))
            )
        self.assertEqual(response.status_code, 200)
        
    def test_response_status_code_404_when_market_does_not_exist(self):
        response = self.client.get(
            reverse('market:traders_in_market', args=('VERYBADID',))
            )
        self.assertEqual(response.status_code, 404)
   
    def test_empty_dict_when_no_trader_in_market(self):
        response = self.client.get(
            reverse('market:traders_in_market', args=(self.empty_market.market_id,))
            )
        self.assertEqual(response.json(), {"traders": []}) 
   
    def test_one_trader_in_given_market(self):
        self.assertEqual(Trader.objects.all().count(),2)
        response = self.client.get(
            reverse('market:traders_in_market', args=(self.market.market_id,))
        )
        self.assertEqual(response.json(), {"traders": ["trader_name"]})

    def test_two_traders_in_given_market(self):
        Trader.objects.create(market=self.market, name="third_trader_name")

        self.assertEqual(Trader.objects.all().count(),3)
        response = self.client.get(
            reverse('market:traders_in_market', args=(self.market.market_id,))
        )
        self.assertEqual(response.json(), {"traders": ["trader_name", "third_trader_name"]})


class TradersThisRoundViewTest(TestCase):

    def test_response_status_code_404_when_market_does_not_exist(self):
        url = reverse('market:traders_this_round', args=('VERYBADID',)) + '?round_num=0'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_response_status_code_200_when_params_are_good(self):
        market = Market.objects.create(round=0)
        url = reverse('market:traders_this_round', args=(market.market_id,))  
        response = self.client.get(url) 
        self.assertEqual(response.status_code, 200)

    def test_zero_trader_in_market_returns_json_with_empty_list(self):    
        market = Market.objects.create(round=0)
        url = reverse('market:traders_this_round', args=(market.market_id,))  
        response = self.client.get(url) 
        self.assertIsInstance(response, JsonResponse)
        data = response.json()
        self.assertIsInstance(data, dict)
        traders = data['traders']
        self.assertIsInstance(traders, list)
        self.assertEqual(traders, [])

    def test_one_trader_in_other_market_this_round_returns_empty_list(self):    
        market1 = Market.objects.create(round=5)
        trader1 = Trader.objects.create(market=market1, name="testtrader")
        Trade.objects.create(market=market1, trader=trader1, unit_price=1, round=5)
        market2 = Market.objects.create(round=5)
        url = reverse('market:traders_this_round', args=(market2.market_id,))  
        traders = self.client.get(url).json()['traders'] 
        self.assertEqual(traders, [])

    def test_one_trader_in_this_market_other_round_returns_empty_list(self):
        market1 = Market.objects.create(round=2)
        trader1 = Trader.objects.create(market=market1, name="testtrader")
        Trade.objects.create(
            market=market1, trader=trader1, unit_price=1, round=1)
        url = reverse('market:traders_this_round', args=(
            market1.market_id,))
        traders = self.client.get(url).json()['traders']
        self.assertEqual(traders, [])
 
    def test_one_trader_in_this_market_this_round_returns_one_trader(self):
        market1 = Market.objects.create(round=1)
        trader1 = Trader.objects.create(market=market1, name="testtrader")
        Trade.objects.create(
            market=market1, trader=trader1, unit_price=1, round=1)
        url = reverse('market:traders_this_round', args=(
            market1.market_id,))
        traders = self.client.get(url).json()['traders']
        self.assertEqual(traders, ['testtrader'])


    def test_correct_traders_get_chosen_no_round_in_url(self):
        market = Market.objects.create(round=0)
        trader1 = Trader.objects.create(market=market, name="TestName1")
        trader2 = Trader.objects.create(market=market, name="TestName2")
        Trade.objects.create(
            market=market, trader=trader1, unit_price=1, round=0)
        Trade.objects.create(
            market=market, trader=trader2, unit_price=1, round=0)
        Trade.objects.create(
            market=market, trader=trader2, unit_price=1, round=1)

        url = reverse('market:traders_this_round', args=(
            market.market_id,))
        traders = self.client.get(url).json()['traders']
        self.assertEqual(traders, ['TestName1','TestName2'])

        market.round += 1
        market.save()
        url = reverse('market:traders_this_round', args=(
        market.market_id,))
        traders = self.client.get(url).json()['traders']
        self.assertEqual(traders, ['TestName2'])

        market.round += 1
        market.save()
        url = reverse('market:traders_this_round', args=(
            market.market_id,))
        traders = self.client.get(url).json()['traders']
        self.assertEqual(traders, [])


class AllTradesViewTest(TestCase):
    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:all_trades', args=('BARMARKETID',))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_response_status_code_200_when_market_exists_and_there_is_atleast_one_trade_in_db(self):
        market = Market.objects.create()
        trader = Trader.objects.create(
            name='Joe', market=market, prod_cost=100, money=5000)
        Trade.objects.create(market=market, trader=trader, unit_price=3, unit_amount=10)
        url = reverse('market:all_trades', args=(market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_one_trader_has_made_one_trade_this_round(self):
        market = Market.objects.create(alpha=10, beta=10, theta=10, min_cost=50, max_cost=200, round=0)
        trader = Trader.objects.create(name='Joe', market=market, prod_cost=100, money=5000)
        Trade.objects.create(market=market, trader=trader, unit_price=3, unit_amount=10)
        url = reverse('market:all_trades', args=(market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        # round goes up by one
        self.assertEqual(Market.objects.all().count(), 1)
        market_now = Market.objects.first()
        self.assertEqual(market_now.round, 1)

        # a stats object has been saved to db
        self.assertEqual(Stats.objects.all().count(),1)
        stat = Stats.objects.first()
        self.assertEqual(stat.market, market)
        self.assertEqual(stat.trader, trader)
        self.assertEqual(stat.round, 0)

        # traders saldo changes by the calculated profit
        self.assertEqual(Trader.objects.all().count(),1)
        trader_now = Trader.objects.first()
        self.assertEqual(trader_now.money, 5000 + stat.profit)       

        # json-response looks good
        self.assertEqual(response.json()['traders'], ['Joe'])
        self.assertEqual(float(response.json()['profit'][0]), stat.profit)

        

class CurrentRoundViewTest(TestCase):

    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:current_round', args=('BARMARKETID',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_response_status_code_200_when_market_exists(self):
        market = Market.objects.create()
        url = reverse('market:current_round', args=(market.market_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_returns_correct_non_zero_round(self):
        market = Market.objects.create(round=11)
        url = reverse('market:current_round', args=(market.market_id,))
        response = self.client.get(url)
        self.assertEqual(response.json(), {"round": 11})

class DownloadViewTest(TestCase):
    # heck for cases, where not all traders have made trades in all rounds
    # check for case where no trades
    pass
