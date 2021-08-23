"""
To run all tests: $ manage.py test
To run only one test in a specific class in test_views:
$ docker-compose exec web python manage.py test market.tests.test_views.MyTestClass.my_test_function 
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade, RoundStat
from ..forms import TraderForm
from ..helpers import filter_trades
from decimal import Decimal
from .factories import TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory, TraderFactory, UserFactory, MarketFactory


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


class CreateMarketViewGETRequestTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    def test_view_url_exits_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    def test_login_required(self):
        """ User not logged in will be redirected to login page """
        self.client.logout()
        response = self.client.get(reverse('market:create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
                         '/accounts/login/?next=/create/')


class CreateMarketViewPOSTRequestTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

        # valid post data
        self.data = {
            'product_name_singular': 'baguettes',
            'product_name_plural': 'baguettes',
            'initial_balance': 5000,
            'alpha': 21.4024,
            'beta': 44.2123,
            'theta': 2.0105,
            'min_cost': 11,
            'max_cost': 144,
            'max_rounds': 15,
            'endless': False

        }

    def test_market_is_created_when_data_is_valid(self):
        """ 
        A market is created when posting valid data & logged in user is set as market's creator 
        After successfull creation, client is redirected to monitor page
        """
        response = self.client.post(
            reverse('market:create'), self.data)
        self.assertEqual(Market.objects.all().count(), 1)
        market = Market.objects.first()
        self.assertEqual(market.created_by, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:monitor', args=(market.market_id,)))

    def test_no_market_is_created_when_min_cost_bigger_than_max_cost_and_error_mgs_is_generated(self):
        """ data is invalid """
        self.data['min_cost'] = 200
        response = self.client.post(
            reverse('market:create'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Market.objects.all().count(), 0)
        self.assertContains(
            response, "Min cost can&#x27;t be bigger than max cost")

    def test_no_market_is_created_when_alpha_not_defined_and_error_mgs_is_generated(self):
        """ data is invalid """
        self.data['alpha'] = ''
        response = self.client.post(reverse('market:create'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Market.objects.all().count(), 0)
        self.assertContains(response, "Dette felt er påkrævet")

    def test_error_mgs_shown_to_user_when_alpha_bigger_than_9999999999(self):
        """ 
        In the model, there are some constraints on alpha, beta and theta. They can't be bigger than 9999999999.9999
        Choosing alpha = 10000000000 in the create form should should create an understandable message to the user,
        not a database-error. 
        """

        self.data['alpha'] = 10000000000

        response = self.client.post(
            reverse('market:create'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Der må maksimalt være 10 cifre før kommaet.")

    def test_if_user_chooses_negative_min_cost_he_gets_a_good_feedback_message(self):
        """ 
        In the model, min_cost and max_cost are set as positive integers. 
        If the users chooses beta negative, this should not cast a database error, but a nice feedback message
        """

        self.data['min_cost'] = -11

        response = self.client.post(
            reverse('market:create'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Denne værdi skal være større end eller lig 0.01.")

    def test_if_user_chooses_negative_max_rounds_he_gets_a_good_error_message(self):
        """ 
        Max_rounds must be an integer >= 1. 
        """

        self.data['max_rounds'] = -4

        response = self.client.post(
            reverse('market:create'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There must be at least 1 round")


class JoinViewTestGETRequests(TestCase):

    def test_view_url_exists_at_proper_name_uses_proper_template_and_has_correct_content(self):
        response = self.client.get(reverse('market:join'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/join.html'),
        html = response.content.decode('utf8')
        self.assertNotIn('KXZCVCZL', html)
        self.assertIsInstance(response.context['form'], TraderForm)

    def test_context_form_when_market_id_is_in_GET(self):
        response = self.client.get(
            reverse('market:join') + "?market_id=KXZCVCZL")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TraderForm)

        html = response.content.decode('utf8')
        self.assertIn('name="market_id" value="KXZCVCZL"', html)

    def test_notify_users_who_have_already_joined_a_market(self):
        market = MarketFactory()
        session = self.client.session
        session['trader_id'] = 3
        session['market_id'] = 'ABCDEF'
        session['username'] = 'Alberte'
        session.save()

        response = self.client.get(
            reverse('market:join'))

        html = response.content.decode('utf8')
        # user should somehow be informed, that he has already joined the market with this id
        self.assertIn("ABCDEF", html)
        self.assertIn("Alberte", html)


class JoinViewTestPOSTRequests(TestCase):

    def test_proper_behavior_when_no_market_id_in_form(self):
        response = self.client.post(reverse('market:join'), {
                                    'username': 'Helle', 'market_id': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)

        html = response.content.decode('utf8')
        error_english = "This field is required." in html
        error_danish = "Dette felt er påkrævet." in html
        self.assertTrue(error_english or error_danish, html)

        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behavior_when_no_username_in_form(self):
        response = self.client.post(reverse('market:join'), {
                                    'name': '', 'market_id': 'SOME_MARKET_ID'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)

        error_danish = "Dette felt er påkrævet."
        self.assertContains(response, error_danish)
        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behavior_when_no_market_with_posted_market_id(self):
        market_id_with_no_referent = 'BAD_MARKET_ID'
        response = self.client.post(reverse('market:join'), {
                                    'name': 'Hanne', 'market_id': market_id_with_no_referent})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)
        self.assertContains(
            response, '<strong>There is no market with this ID</strong>')
        self.assertEqual(Trader.objects.all().count(), 0)

    def test_proper_behaviour_and_nice_feedback_message_when_username_not_available(self):
        market = MarketFactory()
        TraderFactory(market=market, name="jonna")

        response = self.client.post(reverse('market:join'), {
                                    'name': 'jonna', 'market_id': market.market_id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('trader_id' in self.client.session)
        self.assertContains(response,
                            'There is already a trader with this name on the requested market. Please select another name')
        self.assertEqual(Trader.objects.all().count(), 1)

    def test_new_trader_created_when_form_is_valid(self):
        market = MarketFactory()
        response = self.client.post(reverse('market:join'), {
                                    'name': 'Hanne', 'market_id': market.market_id})
        self.assertEqual(Trader.objects.all().count(), 1)
        new_trader = Trader.objects.first()
        self.assertEqual(new_trader.market, market)
        self.assertEqual(new_trader.balance, market.initial_balance)
        self.assertTrue('trader_id' in self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:play'))

    def test_new_trader_who_enters_game_late_created_with_forced_trades_in_previous_rounds(self):
        # a market is in round 3
        market = MarketFactory(round=3)

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

        # The current balance of the trader be equal the initial balance
        self.assertEqual(hanne.balance, market.initial_balance)

        # status code and redirect are corrext
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:play'))


class MonitorViewGETRequestsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by test methods in class
        cls.user = UserFactory()
        cls.market = MarketFactory(created_by=cls.user)

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

    def test_view_url_exists_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(
            reverse('market:monitor', args=(self.market.market_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/monitor.html'),

    def test_market_is_in_context(self):
        response = self.client.get(
            reverse('market:monitor', args=(self.market.market_id,)))
        self.assertEqual(
            response.context['market'].market_id, self.market.market_id)
        self.assertEqual(response.context['market'].round, 0)

    def test_bad_market_id_raises_404(self):
        response = self.client.get(
            reverse('market:monitor', args=('BAD_MARKET_ID',)))
        self.assertEqual(response.status_code, 404)


class MonitorViewPOSTRequestsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by test methods in class
        cls.user = UserFactory()

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:monitor', args=('BADMARKETID',))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_redirect_to_same_url_when_good_arguments(self):
        """ Redirect to monitor view after successful post-request """
        # At least one trade has to have been made this round before post-request
        market = MarketFactory(created_by=self.user)
        trader = TraderFactory(market=market)
        trade = UnProcessedTradeFactory(round=0, trader=trader)
        self.assertEqual(trade.round, trade.trader.market.round)

        url = reverse('market:monitor', args=(trade.trader.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url)

    def test_one_trader_has_made_one_trade_this_round(self):

        # Some trader makes a trade in round 7
        market = MarketFactory(round=7, created_by=self.user)
        trader = TraderFactory(market=market)
        trade = UnProcessedTradeFactory(trader=trader, round=7)

        # At this point, most fields of the trade should be none
        self.assertEqual(trade.round, 7)
        self.assertEqual(trade.profit, None)
        self.assertEqual(trade.demand, None)
        self.assertEqual(trade.units_sold, None)
        self.assertEqual(trade.balance_after, None)

        # The teacher finishes the round
        url = reverse('market:monitor', args=(trade.trader.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url)

        # The profit,balance should now be on the trade object
        trade.refresh_from_db()
        self.assertEqual(trade.round, 7)
        self.assertIsInstance(trade.balance_after, Decimal)
        self.assertIsInstance(trade.profit, Decimal)
        self.assertIsInstance(trade.units_sold, int)
        self.assertIsInstance(trade.demand, int)

        # the round of the market should be 7+1=8
        market.refresh_from_db()
        self.assertEqual(market.round, 8)

    def test_monitor_view_created_forced_moves_for_inactive_player(self):
        # There is a market in round 7 & two traders in this market
        market = MarketFactory(round=7, created_by=self.user)

        trader1 = TraderFactory(market=market)
        trader2 = TraderFactory(market=market, balance=123456)

        # trader1 makes a trade...
        trade = TradeFactory(trader=trader1, round=7)

        # this trade is not saved as a forced trade
        self.assertEqual(trade.was_forced, False)

        # trader2 has not made any trades
        self.assertEqual(Trade.objects.filter(trader=trader2).count(), 0)

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


class MonitorViewPostRequestMultipleUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by test methods in class
        cls.user = UserFactory()

    def setUp(self):
        # log in user before each test
        self.client.login(username=self.user.username,
                          password='defaultpassword')

        self.market = MarketFactory(
            initial_balance=5000,
            alpha=21.402,
            beta=44.2,
            theta=2.0105,
            round=1,
            created_by=self.user)

        # 5 players in the market
        self.christian = TraderFactory(name="christian", market=self.market)
        self.martin = TraderFactory(name="martin", market=self.market)
        self.nadja = TraderFactory(name="nadja", market=self.market)
        self.jens = TraderFactory(name="jens", market=self.market)
        self.kristian = TraderFactory(name="kristian", market=self.market)

        # round 0 is over, and these trades in round 0 have been created properly
        c0 = TradeFactory(trader=self.christian, round=0,
                          unit_price=9, unit_amount=125)
        m0 = TradeFactory(trader=self.martin, round=0,
                          unit_price=10, unit_amount=19)
        n0 = TradeFactory(trader=self.nadja, round=0,
                          unit_price=10, unit_amount=29)
        k0 = TradeFactory(trader=self.kristian, round=0,
                          unit_price=10, unit_amount=29)

        # The 3 traders have chosen amount and price for round 1 (profit and balance_after_not_calculated_yet)
        self.c1 = UnProcessedTradeFactory(
            trader=self.christian, round=1, unit_price=11, unit_amount=150)
        self.m1 = UnProcessedTradeFactory(
            trader=self.martin, round=1, unit_price=9, unit_amount=200)
        self.n1 = UnProcessedTradeFactory(
            trader=self.nadja, round=1, unit_price=11, unit_amount=31)
        self.k1 = UnProcessedTradeFactory(
            trader=self.kristian, round=1, unit_price=17, unit_amount=31)

    def test_players_are_ready(self):
        self.assertTrue(self.christian.is_ready())
        self.assertTrue(self.martin.is_ready())
        self.assertTrue(self.nadja.is_ready())
        self.assertTrue(self.kristian.is_ready())

        num_ready_traders = filter_trades(
            market=self.market, round=self.market.round).count()
        self.assertEqual(num_ready_traders, 4)

    def test_correct_response_code_and_location_after_post_request(self):
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], url)

    def test_balance_and_profit_of_trades_updates(self):
        self.assertEqual(self.c1.balance_after, None)
        self.assertEqual(self.m1.balance_after, None)
        self.assertEqual(self.n1.balance_after, None)
        self.assertEqual(self.k1.balance_after, None)

        self.assertEqual(self.c1.profit, None)
        self.assertEqual(self.m1.profit, None)
        self.assertEqual(self.n1.profit, None)
        self.assertEqual(self.k1.profit, None)

        url = reverse('market:monitor', args=(self.market.market_id,))

        response = self.client.post(url)
        self.c1.refresh_from_db()
        self.m1.refresh_from_db()
        self.n1.refresh_from_db()
        self.k1.refresh_from_db()

        self.assertIsInstance(self.c1.balance_after, Decimal)
        self.assertIsInstance(self.m1.balance_after, Decimal)
        self.assertIsInstance(self.n1.balance_after, Decimal)
        self.assertIsInstance(self.k1.balance_after, Decimal)

        self.assertIsInstance(self.c1.profit, Decimal)
        self.assertIsInstance(self.m1.profit, Decimal)
        self.assertIsInstance(self.n1.profit, Decimal)
        self.assertIsInstance(self.k1.profit, Decimal)

    def test_market_avg_price_has_been_calculated_and_saved(self):
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        self.assertTrue(RoundStat.objects.filter(
            round=1, market=self.market).exists())
        r1stat = RoundStat.objects.get(round=1, market=self.market)
        self.assertEqual(r1stat.avg_price, (9+11+11+17)/4)

    def test_market_is_in_round_2(self):
        self.market.refresh_from_db()
        self.assertEqual(self.market.round, 1)
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.market.refresh_from_db()
        self.assertEqual(self.market.round, 2)

    def test_correct_num_trades_in_db(self):
        num_trades = Trade.objects.all().count()
        self.assertEqual(num_trades, 8)


class PlayViewGetRequestTest(TestCase):

    def test_no_trader_id_in_session_redirects_to_join(self):

        # some client who has not joined tries to access the wait page
        response = self.client.get(reverse('market:play'))

        # he should be redirected to the join page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_no_errors_and_time_to_wait_return_play_template_with_wait_content(self):
        # some market is in round 0
        market = MarketFactory(round=0)

        # a user has joined properly
        trader = TraderFactory(market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session['username'] = 'Hans'
        session.save()

        # the user has made a trade in this round (and should now be waiting)
        TradeFactory(trader=trader, round=0)
        self.assertEqual(Trade.objects.filter(
            trader=trader, round=0).count(), 1)

        # user goes to play url and should get play-template shown with wait equal true in context

        response = self.client.get(
            reverse('market:play'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),
        self.assertTrue(response.context.get('wait'))

        # there should now be a message saying that the user i waiting
        html = response.content.decode('utf8')
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "success")
        self.assertTrue(
            "Du har lavet din handel" in message.message)

        # This is round 0, so no data from last round should be shown
        self.assertNotIn('last round', html)
        self.assertNotIn('Last round', html)
        self.assertFalse(response.context.get('show_last_round_data'))

        # --- no trade history should not be shown either
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
        market = MarketFactory(round=4)

        # a user has joined properly
        trader = TraderFactory(market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session['username'] = 'Hans'
        session.save()

        # the user has made a trade in_last_round
        TradeFactory(trader=trader, round=3, unit_price=Decimal('134.98'))

        # user goes to play url
        response = self.client.get(reverse('market:play'))

        # The user has not traded in this round so he should get back play template with wait=false in context
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/play.html'),
        self.assertFalse(response.context.get('wait'))

        # template should contain data from last round
        html = response.content.decode('utf8')
        self.assertIn("134.98", html)

        # template should not contain the words wait or Wait
        html = response.content.decode('utf8')
        self.assertNotIn("wait", html)
        self.assertNotIn("Wait", html)

        # template should contain a submit button
        html = response.content.decode('utf8')
        self.assertIn("submit", html)

        # player did make a trade in the last round and hence show_last_round_data should be true
        self.assertTrue(response.context.get('show_last_round_data'))

    def test_proper_behavior_in_round_4_when_user_has_made_trade_in_this_but_NOT_in_last_round(self):
        """
        User is in round 4. He traded in round 2, but not in round 3, and not yet in round 4. 
        """
        # some market is in round 4
        market = MarketFactory(round=4)

        # a user has joined properly
        trader = TraderFactory(market=market)
        session = self.client.session
        session['trader_id'] = trader.pk
        session['username'] = 'Hans'
        session.save()

        # the user has made a trade in round 2
        TradeFactory(trader=trader, round=2)

        # the user has not traded in round 3, so a forced trade has been created
        ForcedTradeFactory(trader=trader, round=3)

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

        # player did not make a trade in the last round and hence show_last_round_data should be false
        self.assertFalse(response.context.get('show_last_round_data'))

        # template should contain a submit button
        self.assertIn("submit", html)

    def test_form_attributes_are_set_correctly(self):
        """
        The form fields should have their max values determined by the market and traders
        """
        market = MarketFactory(round=4, max_cost=3)

        # a user has joined properly
        trader = TraderFactory(market=market, balance=101, prod_cost=2)
        session = self.client.session
        session['trader_id'] = trader.pk
        session['username'] = 'Hans'
        session.save()

        # user made a real trade in round 3(last round)
        TradeFactory(trader=trader, round=3, unit_price=4, unit_amount=12)

        # user goes to play url
        response = self.client.get(reverse('market:play'))

        form = response.context['form']

        # we expect the max input value of unit_price to be 5* market.max_cost = 15
        self.assertIn('max="15.00"', str(form))
        self.assertNotIn('max="16.00"', str(form))

        # we expect the max input value of unit_amount to be floor(trader.balance/trader.prod_cost) = floor(101/2) = 50.00
        self.assertIn('max="50"', str(form))
        self.assertNotIn('max="53"', str(form))

    # def test_game_over_when_rounds_equals_max_round(self):
    #     """
    #     When game is over, user should be notified
    #     """
    #     market = MarketFactory(round=4, max_rounds=4)

    #     # a user has joined properly
    #     trader = TraderFactory(market=market, balance=101, prod_cost=2)
    #     session = self.client.session
    #     session['trader_id'] = trader.pk
    #     session['username'] = 'Hans'
    #     session.save()

    #     # user goes to play url
    #     response = self.client.get(reverse('market:play'))
    #     self.assertContains(
    #         response, '.... ')
    #
    #  ......Just realized that this test will not work before merge of previous commit....

class PlayViewPOSTRequestTest(TestCase):

    def test_post_market_id_not_found_redirects_to_join(self):
        # client this to go the play page without having joined a market
        response = self.client.post(
            reverse('market:play'))
        # client should be redirected to join
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:join'))

    def test_if_all_data_is_good_then_save_trade_and_redirect_to_play(self):
        trader = TraderFactory()

        session = self.client.session
        session['trader_id'] = trader.pk
        session.save()

        # the client sends in a trade form with valid data
        response = self.client.post(
            reverse('market:play'), {'unit_price': Decimal('11.00'), 'unit_amount': '45'})
        self.assertEqual(Trade.objects.all().count(), 1)

        # we check that the new trade object has correct properties
        trade = Trade.objects.first()
        self.assertEqual(trade.unit_price, Decimal('11.00'))
        self.assertEqual(trade.unit_amount, 45)
        self.assertEqual(trade.trader, trader)
        self.assertEqual(trade.round, trade.trader.market.round)
        self.assertFalse(trade.was_forced)
        self.assertEqual(trade.profit, None)
        self.assertFalse(trade.balance_after, None)

        # after a successful post request, we should redirect to play
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('market:play')
        self.assertEqual(response['Location'], expected_redirect_url)


class CurrentRoundViewTest(TestCase):

    def test_response_status_code_404_when_market_does_not_exists(self):
        url = reverse('market:current_round', args=('BARMARKETID',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_response_status_code_200_when_market_exists(self):
        market = MarketFactory()
        url = reverse('market:current_round', args=(market.market_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_returns_correct_non_zero_round(self):
        market = MarketFactory(round=11)
        url = reverse('market:current_round', args=(market.market_id,))
        response = self.client.get(url)
        self.assertEqual(response.json(), {"round": 11})


class MyMarketsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

    def test_login_required(self):
        """ user not logged in will be redirected to login page """
        self.client.logout()
        response = self.client.get(reverse('market:my_markets'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
                         '/accounts/login/?next=/my_markets/')

    def test_no_markets_empty_template(self):
        """ logged in user will see correct template """
        response = self.client.get(reverse('market:my_markets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/my_markets.html')

        # print(self.reponse.context)

    def test_no_markets_empty_template(self):
        """ User should not see markets created by other user """
        market = MarketFactory()  # some market created by anouther user
        response = self.client.get(reverse('market:my_markets'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Du har endnu ikke oprettet nogen markeder')
        self.assertNotContains(response, market.market_id)

    def test_user_has_created_a_market(self):
        """ User has created a market so reponse should contain info on this market """
        market = MarketFactory(created_by=self.user)
        response = self.client.get(reverse('market:my_markets'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, 'Du har endnu ikke oprettet nogen markeder')
        self.assertContains(response, market.market_id)
        #html = response.content.decode('utf8')


class TraderTableTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.market = MarketFactory(created_by=cls.user)

    def setUp(self):
        """ log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')


class MarketEditTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):

        self.market = MarketFactory(created_by=self.user, alpha=105.55)

        # log in user before each test """
        self.client.login(username=self.user.username,
                          password='defaultpassword')

    ###################### get requests ############################
    def test_page_exits_and_uses_template(self):
        url = reverse('market:market_edit', args=(self.market.market_id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/market_edit.html')

    def test_user_has_no_permission_to_edit_other_market(self):
        """
        User only has permission to edit the markets she has created
        """
        other_market_not_created_by_client = MarketFactory()

        url = reverse('market:market_edit', args=(
            other_market_not_created_by_client.market_id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('market:home'))

    ###################### post requests ############################

    def test_valid_post_data_updates_market_and_redirects(self):
        data = {'product_name_singular': 'surdejsbolle',
                'product_name_plural': 'surdejsboller', 'alpha': 14, 'beta': 10, 'theta': 32}

        url = reverse('market:market_edit', args=(self.market.market_id,))
        response = self.client.post(url, data=data)

        self.market.refresh_from_db()
        self.assertEqual(float(self.market.alpha), 14)
        self.assertEqual(self.market.product_name_singular, 'surdejsbolle')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse(
            'market:monitor', args=(self.market.market_id,)))

    def test_invalid_post_data_does_not_update_market(self):
        """
        alpha is negative, so form is invalid. No values should be updated in this case
        """

        self.client.login(username='somename', password='testpass123')

        data = {'product_name_singular': 'surdejsbolle',
                'product_name_plural': 'surdejsboller', 'alpha': -3, 'beta': 10, 'theta': 32}

        url = reverse('market:market_edit', args=(self.market.market_id,))
        response = self.client.post(url, data=data)

        self.market.refresh_from_db()
        # alpha has not changed
        self.assertEqual(float(self.market.alpha), 105.55)
        self.assertEqual(self.market.product_name_singular,
                         'baguette')  # product name has not changed

        self.assertEqual(response.status_code, 200)  # return template
        self.assertTemplateUsed(response, 'market/market_edit.html')
