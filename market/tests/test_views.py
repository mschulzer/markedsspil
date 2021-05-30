# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade
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
        
    def test_new_trader_who_enters_game_late_created_with_forced_trades_in_previous_rounds(self):
        market = Market.objects.create(round=3)
        response = self.client.post(reverse('market:join'), {
                                    'username': 'Hanne', 'market_id': market.market_id})

        all_trades = Trade.objects.all()
        self.assertEqual(all_trades.count(), 3)

        self.assertEqual(all_trades[0].trader.name, 'Hanne')
        self.assertEqual(all_trades[0].unit_price, 0)
        self.assertEqual(all_trades[0].unit_amount, 0)

        self.assertEqual(all_trades[0].was_forced, True)
        self.assertEqual(all_trades[2].profit, 0)

        self.assertEqual(all_trades[1].was_forced, True)
        self.assertEqual(all_trades[2].was_forced, True)

        self.assertEqual(all_trades[2].balance_after, 5000)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:play', args=(market.market_id,)))

class MonitorViewGETRequestsTest(TestCase):
 
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()

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

    def test_custom_template_tags(self):
        trader = Trader.objects.create(market=self.market)
        trade = Trade.objects.create(trader=trader)
        response = self.client.get(
            reverse('market:monitor', args=(self.market.market_id,)))
        html = response.content.decode('utf8')
        self.assertIn("Unit Price", html)
        self.assertNotIn("unit_price", html)


class MonitorViewPOSTRequestsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods in class
        cls.market = Market.objects.create()
        cls.trader = Trader.objects.create(
            name='Joe', market=cls.market)

        Trade.objects.create(trader=cls.trader)
        cls.url = reverse('market:monitor', args=(cls.market.market_id,))

    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:monitor', args=('ASDFGHJK',))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_redirect_to_same_url_when_good_arguments(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.url) 


class MonitorViewPOSTRequestsExtraTest(TestCase):
    
    
    def test_one_trader_has_made_one_trade_this_round(self):

        # There is a market in round 7 & a trader in this market
        market = Market.objects.create(round=7)
        trader = Trader.objects.create(
            name='Joe2', market=market)

        # The trader makes a trade
        trade = Trade.objects.create(trader=trader)
        trade.save()
        
        # At this point, the balance and the profit of the trade should be none
        self.assertEqual(trade.round, 7)
        self.assertEqual(trade.trader.name, 'Joe2')
        self.assertEqual(trade.balance_after, None)
        self.assertEqual(trade.profit, None)
        
        # The teacher finishes the round
        trades = Trade.objects.filter(round=market.round).filter(market=market)
        self.assertEqual(trades.count(), 1)
        self.assertEqual(trades.first().market, market)
        self.assertEqual(trades.first().round, 7)

        self.assertEqual(market.round, 7)

        url = reverse('market:monitor', args=(market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url) 

        # the round number of the market should now be 8
        # This assertion is only true when I query the market again... why?
        market_now = Market.objects.first()  
        self.assertEqual(market_now.round, 8) 

        # The profit and balance should now be on the trade object
        # The following assertion only works if I query the market again... why?

        trade_now = Trade.objects.filter(market=market).first()
        self.assertEqual(trade_now.balance_after, 5000)
        self.assertEqual(trade_now.profit, 0)

    def test_monitor_view_created_forced_moves_for_inactive_player(self):
        # There is a market in round 7 & a trader in this market
        market = Market.objects.create(round=7)
        trader = Trader.objects.create(
            name='Hansi', market=market)

        # the trader has not made any trades...
        self.assertEqual(Trade.objects.filter(trader=trader).count(),0)
        
        # The teacher finishes the round...
        url = reverse('market:monitor', args=(market.market_id,))
        response = self.client.post(url)

        # Reponse codes and redict location looks good
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url) 

        # A forced trade for round 7 has been created
        trade = Trade.objects.get(trader=trader)
        self.assertEqual(trade.was_forced, True)
        self.assertEqual(trade.round, 7)
        self.assertEqual(trade.profit, 0)






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
        self.assertFalse(trade.was_forced)
        self.assertEqual(trade.profit, None)
        self.assertFalse(trade.balance_after, None)

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

class TraderAPITest(TestCase):

    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:trader_api', args=('BARMARKETID',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_response_status_code_200_when_market_exists(self):
        market = Market.objects.create()
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.status_code, 200)

    def test_empty_json_when_no_trader_in_market(self):
        market = Market.objects.create()
        response = self.client.get(
            reverse('market:trader_api', args=(
                market.market_id,))
        )
        json = response.json()
        self.assertEqual(json['traders'],[])
        self.assertEqual(json['num_traders'],0)
        self.assertEqual(json['num_ready_traders'], 0)


    def test_one_trader_in_market_with_no_trade_not_included_in_ready_players(self):
        market = Market.objects.create(round=5)
        Trader.objects.create(market=market, name="joe")
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        json = response.json()
        self.assertEqual(json['traders'][0]['name'], "joe")
        self.assertEqual(json['num_traders'], 1)
        self.assertEqual(json['num_ready_traders'], 0)


    def test_one_trader_in_market_other_round_not_included(self):
        market = Market.objects.create(round=3)
        trader = Trader.objects.create(market=market, name="joe")
        Trade.objects.create(trader=trader)
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.json()['num_ready_traders'],1)

        market.round +=1
        market.save()
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.json()['num_traders'],1)
        self.assertEqual(response.json()['num_ready_traders'],0)

    
    def test_trader_in_different_market_same_round_not_included(self):
        market = Market.objects.create(round=3)
        other_market = Market.objects.create(round=3)
        trader = Trader.objects.create(market=other_market, name="joe")
        Trade.objects.create(trader=trader, unit_price=10)
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.json()['num_traders'],0)

    def test_two_traders_included(self):
        market = Market.objects.create(round=3)
        trader1 = Trader.objects.create(market=market, name="joe")
        trader2 = Trader.objects.create(market=market, name="hansi")
        trader3 = Trader.objects.create(market=market, name="morten")

        Trade.objects.create(trader=trader1)
        Trade.objects.create(trader=trader2)

        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.json()["num_traders"],3)
        self.assertEqual(response.json()["num_ready_traders"],2)

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
    # check for cases, where not all traders have made trades in all rounds
    # check for case where no trades
    pass
