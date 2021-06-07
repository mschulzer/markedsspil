# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade
from ..forms import TraderForm
from ..helpers import filter_trades

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
        error_english = "This field is required." in html
        error_danish = "Dette felt er påkrævet." in html
        self.assertTrue(error_english or error_danish, html)

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
        error_english = "This field is required." in html
        error_danish = "Dette felt er påkrævet." in html
        self.assertTrue(error_english or error_danish, html)

        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behavior_when_no_username_in_form(self):
        response = self.client.post(reverse('market:join'), {
                                    'username': '', 'market_id': 'SOME_MARKET_ID'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)

        html = response.content.decode('utf8')
        error_english = "This field is required." in html
        error_danish = "Dette felt er påkrævet." in html
        self.assertTrue(error_english or error_danish, html)
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
                                    'name': 'Hanne', 'market_id': market.market_id})
        self.assertEqual(Trader.objects.all().count(), 1)
        new_trader = Trader.objects.first()
        self.assertEqual(new_trader.market, market)
        self.assertTrue('trader_id' in self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:play'))
        
    def test_new_trader_who_enters_game_late_created_with_forced_trades_in_previous_rounds(self):
        # a market is in round 3
        market = Market.objects.create(round=3)

        # a players named Hanne tries to join the market (she is late)
        response = self.client.post(reverse('market:join'), {
                                    'name': 'Hanne', 'market_id': market.market_id})
        
        # the trader hanne was created
        hanne = Trader.objects.get(name='Hanne')

        # when hanne joined, 3 forced trades was made for her in previous rounds 
        hannes_trades = hanne.trade_set.all()
        self.assertEqual(hannes_trades.count(), 3)
        for i in range(3):
            self.assertEqual(hannes_trades[i].was_forced, True)
            self.assertEqual(hannes_trades[i].trader.name, 'Hanne')
            self.assertEqual(hannes_trades[i].unit_price, None)
            self.assertEqual(hannes_trades[i].profit, None)
            self.assertEqual(hannes_trades[i].unit_amount, None)
            self.assertEqual(hannes_trades[i].round, i)
            self.assertEqual(hannes_trades[i].balance_after, None)

        # The balance of the trader be equal the initial balance
        self.assertEqual(hanne.balance, Trader.initial_balance)

        # status code and redirect are corrext        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:play'))


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
        market = Market.objects.create(round = 3)
        trader = Trader.objects.create(market=market)
        trade = Trade.objects.create(trader=trader, round=market.round)
        response = self.client.get(
            reverse('market:monitor', args=(market.market_id,)))
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

        Trade.objects.create(trader=cls.trader, round=0)
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
        trade = Trade.objects.create(trader=trader, round=market.round)
        trade.save()
        
        # At this point, the balance and the profit of the trade should be none
        self.assertEqual(trade.round, 7)
        self.assertEqual(trade.trader.name, 'Joe2')
        self.assertEqual(trade.balance_after, None)
        self.assertEqual(trade.profit, None)
        
        # The teacher finishes the round
        trades = filter_trades(market=market, round=market.round)
        self.assertEqual(trades.count(), 1)
        self.assertEqual(trades.first().trader.market, market)
        self.assertEqual(trades.first().round, 7)

        self.assertEqual(market.round, 7)

        url = reverse('market:monitor', args=(market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url) 

        # The profit and balance should now be on the trade object
        trade.refresh_from_db()
        self.assertEqual(trade.balance_after, Trader.initial_balance)
        self.assertEqual(trade.profit, 0)

        # the round of the market should be 7+1=8
        market.refresh_from_db()
        self.assertEqual(market.round, 8)

    def test_monitor_view_created_forced_moves_for_inactive_player(self):
        # There is a market in round 7 & a two traders in this market
        market = Market.objects.create(round=7)
        trader1 = Trader.objects.create(
            name='Hansi', market=market)
        trader2 = Trader.objects.create(
            name='Kwaganzi', market=market)

        # for testing purposes we set a balance for trader 2:
        trader2.balance=123456
        trader2.save()

        # trader1 makes a trade...
        Trade.objects.create(trader=trader1 , round=market.round)

        # this trade is not saved as a forced trade
        self.assertEqual(Trade.objects.get(trader=trader1).was_forced, False)

        # trader2 has not made any trades
        self.assertEqual(Trade.objects.filter(trader=trader2).count(),0)

        # The teacher finishes the round anyway..
        url = reverse('market:monitor', args=(market.market_id,))
        response = self.client.post(url)        

        # Reponse codes and redict location looks good
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url) 

        # A forced trade for trader2 in round 7 has been created
        trade = Trade.objects.get(trader=trader2)
        self.assertEqual(trade.was_forced, True)
        self.assertEqual(trade.round, 7)
        self.assertEqual(trade.profit, None)

        # The balance of trader2 should not be affected by the forced trade
        trader2.refresh_from_db()
        self.assertEqual(trader2.balance, 123456)
        
        # The round num has gone up by round
        market.refresh_from_db()
        self.assertEqual(market.round, 8)


class PlayViewGetRequestTest(TestCase):

    def test_no_trader_id_in_session_redirects_to_join(self):

        # some client who has not joined tries to access the wait page
        response = self.client.get(reverse('market:play'))

        # he should be redirected to the join page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_no_errors_and_time_to_wait_return_wait_template_and_code_200(self):
        # some market is in round 0
        market=Market.objects.create()

        # a user has joined properly
        trader = Trader.objects.create(name='otto', market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()
        
        # the user has made a trade in this round (and should now be waiting)
        Trade.objects.create(trader=trader, round=market.round, profit=345)
        self.assertEqual(Trade.objects.filter(trader=trader, round=0).count(),1)
        
        # user goes to play url and should get play-template shown
        response = self.client.get(
            reverse('market:play'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),

         # template should contain the word Waiting
        html = response.content.decode('utf8')
        self.assertIn("Waiting", html)

        # This is round 0, so no data from last round should be shown
        self.assertNotIn('last round', html)
        self.assertNotIn('Last round', html)

        # --- no trade history should be shown either
        self.assertNotIn('Trade History', html)
        self.assertNotIn('Previous History', html)
        self.assertNotIn('Record', html)


        # Template should not contain a submit button
        self.assertNotIn('submit', html)
        
      
    def test_proper_behavior_in_round_4_when_user_has_made_trade_in_this_and_last_round(self):
        """
        User has traded in round 4, and in round 3.
        """
        # some market is in round 4
        market=Market.objects.create(round=4)

        # a user has joined properly
        trader = Trader.objects.create(name='otto', market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        # the user has made a trade in_last_round
        Trade.objects.create(trader=trader, round=3, profit=3432253, balance_after=12, was_forced=False)
        
        # user goes to play url
        response = self.client.get(reverse('market:play'))

        # The user has not traded in this round so he should get back play temlpate
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),
        
        # template should contain data from last round
        html = response.content.decode('utf8')
        self.assertIn("3432253", html)

         # template should not contain the words wait or Wait  
        html = response.content.decode('utf8')
        self.assertNotIn("wait", html)
        self.assertNotIn("Wait", html)
    
        # template should contain a submit button
        html = response.content.decode('utf8')
        self.assertIn("submit", html)

    def test_proper_behavior_in_round_4_when_user_has_made_trade_in_this_but_NOT_in_last_round(self):
        """
        User is in round 4. Traded in round 2, but not in round 3, and not yet in round 4. 
        """
        # some market is in round 4
        market = Market.objects.create(round=4)

        # a user has joined properly
        trader = Trader.objects.create(name='otto', market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        # the user has made a trade in round 2
        Trade.objects.create(trader=trader, round=2,
                             profit=3432253, balance_after=12, was_forced=False)

        # the user has not traded in round 3, so a forced trade has been created
        Trade.objects.create(trader=trader, round=3, was_forced=True)

        # user goes to play url
        response = self.client.get(reverse('market:play'))

        # The user has not traded in this round so he should get back play temlpate
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),

        html = response.content.decode('utf8')

        # template should not contain the words wait or Wait
        html = response.content.decode('utf8')
        self.assertNotIn("wait", html)
        self.assertNotIn("Wait", html)

        # template should not contain the words last or Last
        html = response.content.decode('utf8')

        # template should contain a submit button
        self.assertIn("submit", html)

        # template should contain profit from round 2
        self.assertIn("3432253", html)
        self.assertIn("----", html)


class PlayViewPOSTRequestTest(TestCase):

    def test_post_market_id_not_found_redirects_to_join(self):
        # client this to go the play page without having joined a market
        response = self.client.post(
            reverse('market:play'))
        # client should be redirected to join
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_all_data_is_good_then_save_trade_and_redirect_to_play(self):
        # some market is in round 0
        market = Market.objects.create()

        # a user has joined properly
        trader = Trader.objects.create(name='otto', market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        self.assertEqual(trader.balance, 5000)
        self.assertEqual(trader.prod_cost, 1)

        # the client sends in a trade form with valid data
        response = self.client.post(
            reverse('market:play'), {'unit_price': '11', 'unit_amount': '45'})
        self.assertEqual(Trade.objects.all().count(), 1)
        
        # we check that the new trade object has correct properties
        trade = Trade.objects.first()
        self.assertEqual(float(trade.unit_price), 11)
        self.assertEqual(trade.unit_amount, 45)
        self.assertEqual(trade.trader.market, market)
        self.assertEqual(trade.trader, trader)
        self.assertEqual(trade.round, 0)
        self.assertFalse(trade.was_forced)
        self.assertEqual(trade.profit, None)
        self.assertFalse(trade.balance_after, None)

        # after a succesfull post request, we should redirect to play
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('market:play')
        self.assertEqual(response['Location'], expected_redirect_url)

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


    def test_one_trade_in_previous_round_not_ready(self):
        # there is a market in round 3 & a trader in this market
        market = Market.objects.create(round=3)
        trader = Trader.objects.create(market=market, name="joe")

        # the trader has made a trade in a previous round (round 2)
        Trade.objects.create(trader=trader, round=2)

        # the api is called to check on trader status
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        # as the trade is not made in this round, there should be zero ready traders
        self.assertEqual(response.json()['num_ready_traders'],0)
        self.assertEqual(response.json()['num_traders'], 1)

    def test_one_trade_in_this_round_ready(self):
        # there is a market in round 3 & a trader in this market
        market = Market.objects.create(round=3)
        trader = Trader.objects.create(market=market, name="joe")

        # the trader has made a trade in this round (round 3)
        Trade.objects.create(trader=trader, round=3)

        # the api is called to check on trader status
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        # as the trade is not made in this round, there should be zero ready traders
        self.assertEqual(response.json()['num_ready_traders'], 1)
        self.assertEqual(response.json()['num_traders'], 1)
    
    def test_trader_in_different_market_same_round_not_included(self):
        market = Market.objects.create(round=3)
        other_market = Market.objects.create(round=3)
        trader = Trader.objects.create(market=other_market, name="joe")
        Trade.objects.create(trader=trader, round=3)
        response = self.client.get(
            reverse('market:trader_api', args=(market.market_id,))
        )
        self.assertEqual(response.json()['num_traders'],0)

    def test_two_traders_included(self):
        market = Market.objects.create(round=3)
        trader1 = Trader.objects.create(market=market, name="joe")
        trader2 = Trader.objects.create(market=market, name="hansi")
        trader3 = Trader.objects.create(market=market, name="morten")

        Trade.objects.create(trader=trader1, round=3)
        Trade.objects.create(trader=trader2, round=3)

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
