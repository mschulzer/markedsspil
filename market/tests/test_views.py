"""
To run all tests:
$ make test

To run all tests in this file:
$ docker-compose run web pytest market/tests/test_views.py

To run only one or some tests:
$ docker-compose run web pytest -k <substring of test function names to run>
"""
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade, RoundStat, UnusedCosts
from ..forms import TraderForm
from ..helpers import filter_trades
from decimal import Decimal
from .factories import TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory, TraderFactory, UserFactory, MarketFactory

import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains

# Test Home view
def test_home_view_post_requests_not_allowed(client):
    url = reverse('market:home')
    response = client.post(url)
    assert response.status_code == 405

def test_home_view_url_exists_at_proper_location_and_uses_proper_template(client):
    response = client.get('/')
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/home.html')

def test_home_view_name_and_template(client):
    response = client.get(reverse('market:home'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/home.html')


### Test Create Market View GET Request
def test_create_view_url_and_template(client, logged_in_user):
    response = client.get('/create/')
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/create.html')

def test_create_view_name_and_template(client, logged_in_user):
    response = client.get(reverse('market:create'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/create.html'),

def test_create_view_login_required(client, logged_in_user):
    """ User not logged in will be redirected to login page """
    client.logout()
    response = client.get(reverse('market:create'))
    assert response.status_code == 302
    assert response['Location'] == '/accounts/login/?next=/create/'

### Test Create Market View POST Request

@pytest.fixture
def create_market_data():
    return {
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


def test_market_is_created_when_data_is_valid(client, logged_in_user, create_market_data):
    """ 
    A market is created when posting valid data & logged in user is set as market's creator 
    Since min_cost < max_cost two new Unused costs are produced
    After successfull creation, client is redirected to monitor page
    """
    response = client.post(reverse('market:create'), create_market_data)
    assert Market.objects.all().count() == 1
    market = Market.objects.first()
    assert (market.created_by == logged_in_user)
    assert (response.status_code == 302)
    assert(response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))

    # min_cost is less than max_cost. Therefore two Unused costs should have been produced after creating the market
    unused_costs = UnusedCosts.objects.all()
    assert (unused_costs.count() == 2)
    # the first unused cost should have value = min_cost
    assert (unused_costs.first().cost == 11)
    assert (unused_costs.first().market == market)
    # the second unused cost should have value = max_cost
    assert (unused_costs.last().cost == 144)

def test_when_min_costs_equals_max_cost_no_unused_costs_are_produced(client, logged_in_user, create_market_data):
    """ 
    A market is created when posting valid data & logged in user is set as market's creator 
    After successfull creation, client is redirected to monitor page. 
    Since min_cost == max_cost not Unused costs are produced
    """
    create_market_data['max_cost'] = 11

    response = client.post(reverse('market:create'), create_market_data)
    assert (Market.objects.all().count() == 1)
    market = Market.objects.first()
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:monitor', args=(market.market_id,)))

    # min_cost is less than max_cost. Therefore two Unused costs should have been produced after creating the market
    unused_costs = UnusedCosts.objects.all()
    assert (unused_costs.count() == 0)

    
def test_no_market_is_created_when_min_cost_bigger_than_max_cost_and_error_mgs_is_generated(client, logged_in_user, create_market_data):
    """ data is invalid """
    create_market_data['min_cost'] = 200
    response = client.post(reverse('market:create'), create_market_data)
    assert response.status_code == 200
    assert Market.objects.all().count() == 0
    assertContains(response, "Min cost can&#x27;t be bigger than max cost")

def test_no_market_is_created_when_alpha_not_defined_and_error_mgs_is_generated(client, logged_in_user, create_market_data):
    """ data is invalid """
    create_market_data['alpha'] = ''
    response = client.post(reverse('market:create'), create_market_data)
    assert response.status_code == 200
    assert Market.objects.all().count() == 0
    assertContains(response, "This field is required.")

def test_error_mgs_shown_to_user_when_alpha_bigger_than_9999999999(client, logged_in_user, create_market_data):
    """ 
    In the model, there are some constraints on alpha, beta and theta. They can't be bigger than 9999999999.9999
    Choosing alpha = 10000000000 in the create form should should create an understandable message to the user,
    not a database-error. 
    """
    create_market_data['alpha'] = 10000000000
    response = client.post(reverse('market:create'), create_market_data)
    assert response.status_code == 200
    assertContains(response, "Ensure that there are no more than 10 digits before the decimal point.")

def test_if_user_chooses_negative_min_cost_he_gets_a_good_feedback_message(client, logged_in_user, create_market_data):
    """ 
    In the model, min_cost and max_cost are set as positive integers. 
    If the users chooses beta negative, this should not cast a database error, but a nice feedback message
    """
    create_market_data['min_cost'] = -11
    response = client.post(reverse('market:create'), create_market_data)
    assert response.status_code == 200
    assertContains(response, "Ensure this value is greater than or equal to 0.01.")

def test_if_user_chooses_negative_max_rounds_he_gets_a_good_error_message(client, logged_in_user, create_market_data):
    """ 
    Max_rounds must be an integer >= 1. 
    """
    create_market_data['max_rounds'] = -4
    response = client.post(reverse('market:create'), create_market_data)
    assert (response.status_code == 200)
    assertContains(response, "There must be at least 1 round")

    
## JoinViewTestGETRequests

def test_view_url_exists_at_proper_name_uses_proper_template_and_has_correct_content(client):
    response = client.get(reverse('market:join'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/join.html'),
    assertNotContains(response, 'KXZCVCZL')
    assert isinstance(response.context['form'], TraderForm)

def test_context_form_when_market_id_is_in_GET(client):
    response = client.get(
        reverse('market:join') + "?market_id=KXZCVCZL")
    assert response.status_code == 200
    assert isinstance(response.context['form'], TraderForm)
    assertContains(response, 'name="market_id" value="KXZCVCZL"')

def test_notify_users_who_have_already_joined_a_market(client, db):
    market = MarketFactory()
    session = client.session
    session['trader_id'] = 3
    session['market_id'] = market.market_id
    session['username'] = 'Alberte'
    session.save()

    response = client.get(reverse('market:join'))

    # user should somehow be informed, that he has already joined the market with this id
    assertContains(response, market.market_id)
    assertContains(response, "Alberte")


## JoinViewTestPOSTRequests

def test_proper_behavior_when_no_market_id_in_form(db, client):
    from django.utils import translation
    translation.activate("en-US")
    
    response = client.post(reverse('market:join'), {
        'username': 'Helle', 'market_id': ''})
    assert response.status_code == 200
    assert 'trader_id' not in client.session
    assertContains(response, "This field is required.")
    assert Trader.objects.all().count() == 0

def test_proper_behavior_when_no_username_in_form(db, client):
    response = client.post(reverse('market:join'), {
                                'name': '', 'market_id': 'SOME_MARKET_ID'})
    assert response.status_code == 200
    assert not ('trader_id' in client.session)
    assertContains(response, "This field is required.")
    assert Trader.objects.all().count() == 0

def test_proper_behavior_when_no_market_with_posted_market_id(db, client):
    market_id_with_no_referent = 'BAD_MARKET_ID'
    response = client.post(reverse('market:join'), {
        'name': 'Hanne', 'market_id': market_id_with_no_referent})
    assert (response.status_code == 200)
    assert not ('trader_id' in client.session)
    assertContains(response, '<strong>There is no market with this ID</strong>')
    assert (Trader.objects.all().count() == 0)

def test_proper_behaviour_and_nice_feedback_message_when_username_not_available(db, client):
    market = MarketFactory()
    TraderFactory(market=market, name="jonna")

    response = client.post(reverse('market:join'), {
                                'name': 'jonna', 'market_id': market.market_id})
    assert (response.status_code == 200)
    assert not ('trader_id' in client.session)
    assertContains(response, 'There is already a trader with this name on the requested market. Please select another name')
    assert (Trader.objects.all().count() == 1)

def test_new_trader_created_when_form_is_valid(db, client):
    market = MarketFactory(min_cost=4, max_cost=4)
    response = client.post(reverse('market:join'), {
                                'name': 'Hanne', 'market_id': market.market_id})
    assert (Trader.objects.all().count() == 1)
    new_trader = Trader.objects.first()
    assert (new_trader.market == market)
    assert (new_trader.balance == market.initial_balance)
    assert ('trader_id' in client.session)
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:play', args=(market.market_id,)))
    # Since min_cost == max_cost ==4, the traders prod_cost should equal 4
    assert (new_trader.prod_cost == 4)

def test_new_trader_who_enters_game_late_created_with_forced_trades_in_previous_rounds(db, client):
    # a market is in round 3
    market = MarketFactory(round=3)

    # a players named Hanne tries to join the market (she is late)
    response = client.post(reverse('market:join'), {
                                'name': 'Hanne', 'market_id': market.market_id})

    # the trader hanne was created
    hanne = Trader.objects.get(name='Hanne')

    # it is registered, that Hanne joined in round 3
    assert (hanne.round_joined == 3)
    
    # when hanne joined, 3 forced trades was made for her in previous rounds
    hannes_trades = hanne.trade_set.all()
    assert (hannes_trades.count() == 3)
    for i in range(3):
        assert (hannes_trades[i].was_forced)
        assert (hannes_trades[i].trader.name == 'Hanne')
        assert (hannes_trades[i].unit_price is None)
        assert (hannes_trades[i].profit is None)
        assert (hannes_trades[i].unit_amount is None)
        assert (hannes_trades[i].round == i)
        assert (hannes_trades[i].balance_after is None)
        assert (hannes_trades[i].balance_before is None)

    # The current balance of the trader be equal the initial balance
    assert (hanne.balance == market.initial_balance)

    # status code and redirect are corrext
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:play', args=(market.market_id,)))


# Test MonitorViewGETRequests

def test_view_url_exists_at_proper_name_and_uses_proper_template(client, db, logged_in_user):
    market = MarketFactory(created_by=logged_in_user)
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/monitor.html'),

def test_monitor_view_user_not_logged_in_has_no_access(client, db, logged_in_user):
    """ Other users (e.g. traders) can't in general access the monitor view"""
    market = MarketFactory(created_by=logged_in_user)
    client.logout()
    other_user = UserFactory(username="olebole")
    client.login(username=other_user.username,
                 password='defaultpassword')
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    # redirect as no access
    assert (response.status_code == 302)

def test_monitor_view_user_has_no_access_to_other_users_market(client, db, logged_in_user):
    """ client who did not create the market only has access to monitor view when the game is over"""
    market = MarketFactory(created_by=logged_in_user)
    client.logout()
    other_user = UserFactory(username="olebole")
    client.login(username=other_user.username,
                      password='defaultpassword')
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    # redirect as no access
    assert (response.status_code == 302)

    # we set game state to game over
    market.round = market.max_rounds
    assert (market.game_over())
    market.save()

    # visitor should now have access to the monitor page
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    assert (response.status_code == 200)

def test_market_is_in_context(client, db, logged_in_user):
    market = MarketFactory(created_by=logged_in_user)
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    assert response.context['market'].market_id == market.market_id
    assert response.context['market'].round == 0

def test_bad_market_id_raises_404(client, db, logged_in_user):
    market = MarketFactory()
    response = client.get(
        reverse('market:monitor', args=('BAD_MARKET_ID',)))
    assert response.status_code == 404


#  MonitorViewPOSTRequests

def test_monitor_view_404_when_market_does_not_exists(client, logged_in_user):
    url = reverse('market:monitor', args=('BADMARKETID',))
    response = client.post(url)
    assert (response.status_code == 404)

def test_redirect_to_same_url_when_good_arguments(client, logged_in_user):
    """ Redirect to monitor view after successful post-request """
    # At least one trade has to have been made this round before post-request
    market = MarketFactory(created_by=logged_in_user)
    trader = TraderFactory(market=market)
    trade = UnProcessedTradeFactory(round=0, trader=trader)
    assert trade.round == trade.trader.market.round

    url = reverse('market:monitor', args=(trade.trader.market.market_id,))
    response = client.post(url)
    assert (response.status_code == 302)
    assert (response['Location'] == url)

def test_one_trader_has_made_one_trade_this_round(client, logged_in_user):

    # Some trader makes a trade in round 7
    market = MarketFactory(round=7, created_by=logged_in_user)
    trader = TraderFactory(market=market)
    trade = UnProcessedTradeFactory(trader=trader, round=7)

    # At this point, most fields of the trade should be none
    assert (trade.round == 7)
    assert (trade.profit is None)
    assert (trade.demand is None)
    assert (trade.units_sold is None)
    assert (trade.balance_after is None)

    # The teacher finishes the round
    url = reverse('market:monitor', args=(trade.trader.market.market_id,))
    response = client.post(url)
    assert (response.status_code == 302)
    assert (response['Location'] == url)

    # The profit,balance should now be on the trade object
    trade.refresh_from_db()
    assert (trade.round == 7)
    assert isinstance(trade.balance_after, Decimal)
    assert isinstance(trade.balance_before, Decimal)
    assert (trade.balance_before == TraderFactory.balance)
    assert isinstance(trade.profit, Decimal)
    assert isinstance(trade.units_sold, int)
    assert isinstance(trade.demand, int)

    # the round of the market should be 7+1=8
    market.refresh_from_db()
    assert (market.round == 8)

def test_monitor_view_created_forced_moves_for_inactive_player(client, logged_in_user):
    # There is a market in round 7 & two traders in this market
    market = MarketFactory(round=7, created_by=logged_in_user)

    trader1 = TraderFactory(market=market)
    trader2 = TraderFactory(market=market, balance=123456)

    # trader1 makes a trade...
    trade = TradeFactory(trader=trader1, round=7)

    # this trade is not saved as a forced trade
    assert not (trade.was_forced)

    # trader2 has not made any trades
    assert (Trade.objects.filter(trader=trader2).count() == 0)

    # The teacher finishes the round anyway..
    url = reverse('market:monitor', args=(market.market_id,))
    response = client.post(url)

    # Reponse codes and redict location looks good
    assert (response.status_code == 302)
    assert (response['Location'] == url)

    # A forced trade for trader2 in round 7 has been created
    trade = Trade.objects.get(trader=trader2)
    assert (trade.was_forced)
    assert (trade.round == 7)
    assert (trade.profit is None)
    assert (trade.balance_before == 123456)
    assert (trade.balance_after == 123456)

    # The balance of trader2 should not be affected by the forced trade
    trader2.refresh_from_db()
    assert (trader2.balance == 123456)

    # The round num has gone up by round
    market.refresh_from_db()
    assert (market.round == 8)


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
        assert (self.christian.is_ready())
        assert (self.martin.is_ready())
        assert (self.nadja.is_ready())
        assert (self.kristian.is_ready())

        num_ready_traders = filter_trades(
            market=self.market, round=self.market.round).count()
        assert (num_ready_traders == 4)

    def test_correct_response_code_and_location_after_post_request(self):
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        assert (response.status_code == 302)
        assert (response['Location'] == url)

    def test_balance_and_profit_of_trades_updates(self):
        assert (self.c1.balance_after is None)
        assert (self.m1.balance_after is None)
        assert (self.n1.balance_after is None)
        assert (self.k1.balance_after is None)

        assert (self.c1.profit is None)
        assert (self.m1.profit is None)
        assert (self.n1.profit is None)
        assert (self.k1.profit is None)

        url = reverse('market:monitor', args=(self.market.market_id,))

        response = self.client.post(url)
        self.c1.refresh_from_db()
        self.m1.refresh_from_db()
        self.n1.refresh_from_db()
        self.k1.refresh_from_db()

        assert isinstance(self.c1.balance_after, Decimal)
        assert isinstance(self.m1.balance_after, Decimal)
        assert isinstance(self.n1.balance_after, Decimal)
        assert isinstance(self.k1.balance_after, Decimal)

        assert isinstance(self.c1.profit, Decimal)
        assert isinstance(self.m1.profit, Decimal)
        assert isinstance(self.n1.profit, Decimal)
        assert isinstance(self.k1.profit, Decimal)

    def test_market_avg_price_has_been_calculated_and_saved(self):
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        assert (RoundStat.objects.filter(
            round=1, market=self.market).exists())
        r1stat = RoundStat.objects.get(round=1, market=self.market)
        assert (r1stat.avg_price == (9+11+11+17)/4)

    def test_market_is_in_round_2(self):
        self.market.refresh_from_db()
        assert (self.market.round == 1)
        url = reverse('market:monitor', args=(self.market.market_id,))
        response = self.client.post(url)
        assert (response.status_code == 302)
        self.market.refresh_from_db()
        assert (self.market.round == 2)

    def test_correct_num_trades_in_db(self):
        num_trades = Trade.objects.all().count()
        assert (num_trades == 8)


# Test PlayViewGetRequest

def test_no_trader_id_in_session_redirects_to_join(client):
    # some client who has not joined tries to access the wait page
    response = client.get(reverse('market:play', args=('SOMEMARKETD',)))

    # he should be redirected to the join page
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:join'))

def test_if_no_errors_and_time_to_wait_return_play_template_with_wait_content(client, db):
    # some market is in round 0
    market = MarketFactory(round=0)

    # a user has joined properly
    trader = TraderFactory(market=market)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # the user has made a trade in this round (and should now be waiting)
    TradeFactory(trader=trader, round=0)
    assert (Trade.objects.filter(
        trader=trader, round=0).count() == 1)

    # user goes to play url and should get play-template shown with wait equal true in context
    response = client.get(reverse('market:play', args=(market.market_id,)))
    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/play.html'),
    assert (response.context.get('wait'))

    # there should now be a message saying that the user i waiting
    html = response.content.decode('utf8')
    message = list(response.context.get('messages'))[0]
    assert (message.tags == "success")
    assert ("You made a trade!" in message.message)

    # This is round 0, so no data from last round should be shown
    assertNotContains(response, 'Text with info about last round choices and results')

    # Template should not contain a submit button
    assertNotContains(response, 'submit')

def test_proper_behavior_in_round_4_when_user_has_made_trade_in_this_and_last_round(client, db):
    """
    User has traded in round 4, and in round 3.
    """
    # some market is in round 4
    market = MarketFactory(round=4)

    # a user has joined properly
    trader = TraderFactory(market=market)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # the user has made a trade in_last_round
    TradeFactory(trader=trader, round=3, unit_price=Decimal('134.98'))

    # user goes to play url
    response = client.get(reverse('market:play', args=(market.market_id,)))

    # The user has not traded in this round so he should get back play template with wait=false in context
    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/play.html'),
    assert not (response.context.get('wait'))

    # template should contain data from last round
    assertContains(response, "134.98")

    # template should not contain the words wait or Wait
    assertNotContains(response, "wait")
    assertNotContains(response, "Wait")

    # template should contain a submit button
    assertContains(response, "submit")

    # template should not contain a link to the monitor view, since game is not over
    assertNotContains(response, f"/{market.market_id}/monitor")

def test_proper_behavior_in_round_4_when_user_has_made_trade_in_this_but_NOT_in_last_round(client, db):
    """
    User is in round 4. He traded in round 2, but not in round 3, and not yet in round 4. 
    """
    # some market is in round 4
    market = MarketFactory(round=4)

    # a user has joined properly
    trader = TraderFactory(market=market)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # the user has made a trade in round 2
    TradeFactory(trader=trader, round=2)

    # the user has not traded in round 3, so a forced trade has been created
    ForcedTradeFactory(trader=trader, round=3)

    # user goes to play url
    response = client.get(reverse('market:play', args=(market.market_id,)))

    # The user has not traded in this round so he should get back play temlpate
    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/play.html'),

    # template should not contain the words wait or Wait
    assertNotContains(response, "wait")
    assertNotContains(response, "Wait")

    # The player should know that he didn't trade last round
    assertContains(response, "You didn't make a trade last round.")

    # template should contain a submit button
    assertContains(response, "submit")

    # template should not contain a link to the monitor view, since game is not over
    assertNotContains(response, f"/{market.market_id}/monitor")


def test_form_attributes_are_set_correctly(client, db):
    """
    The form fields should have their max values determined by the market and traders
    """
    market = MarketFactory(round=4, max_cost=3)

    # a user has joined properly
    trader = TraderFactory(market=market, balance=101, prod_cost=2)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # user made a real trade in round 3(last round)
    TradeFactory(trader=trader, round=3, unit_price=4, unit_amount=12)

    # user goes to play url
    response = client.get(reverse('market:play', args=(market.market_id,)))

    form = response.context['form']

    # we expect the max input value of unit_price to be 5* market.max_cost = 15
    assert ('max="15.00"' in str(form))
    assert not ('max="16.00"' in str(form))

    # we expect the max input value of unit_amount to be floor(trader.balance/trader.prod_cost) = floor(101/2) = 50.00
    assert ('max="50"' in str(form))
    assert ('max="53"' not in str(form))

def test_game_over_when_rounds_equal_max_round(client, db):
    """
    When game is over, the user should be notified about this
    """
    market = MarketFactory(round=4, max_rounds=4, endless=False)

    # a user has joined properly
    trader = TraderFactory(market=market, balance=101, prod_cost=2)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # user goes to play url
    response = client.get(reverse('market:play', args=(market.market_id,)))

    # user is informed about the game state
    assertContains(response, "The game has ended")

    # the player interface does not contain a submit button
    assertNotContains(response, 'submit')

    # the player interface contains a link to the monitor view
    #assertContains(response, f"/{market.market_id}/monitor")


# PlayViewPOSTRequest

def test_post_market_id_not_found_redirects_to_join(client):
    # client tryes to go the play page without having joined a market
    response = client.post(
        reverse('market:play', args=('SOMEMARKETID',)))
    # client should be redirected to join
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:join'))

def test_if_all_data_is_good_then_save_trade_and_redirect_to_play(client, db):
    trader = TraderFactory()

    session = client.session
    session['trader_id'] = trader.pk
    session.save()

    # the client sends in a trade form with valid data
    response = client.post(
        reverse('market:play', args=(trader.market.market_id,)), {'unit_price': Decimal('11.00'), 'unit_amount': '45'})
    assert (Trade.objects.all().count() == 1)

    # we check that the new trade object has correct properties
    trade = Trade.objects.first()
    assert (trade.unit_price == Decimal('11.00'))
    assert (trade.unit_amount == 45)
    assert (trade.trader == trader)
    assert (trade.round == trade.trader.market.round)
    assert not (trade.was_forced)
    assert (trade.profit is None)
    assert (trade.balance_after is None)
    assert (trade.balance_before == TraderFactory.balance)

    # after a successful post request, we should redirect to play
    assert (response.status_code == 302)
    expected_redirect_url = reverse(
        'market:play', args=(trader.market.market_id,))
    assert (response['Location'] == expected_redirect_url)

def test_error_message_to_user_when_invalid_form(client, db):
    trader = TraderFactory()

    session = client.session
    session['trader_id'] = trader.pk
    session.save()

    # the client sends in a trade form with invalid data (unit price is blank)
    response = client.post(
        reverse('market:play', args=('SOMEMARKETID',)), {'unit_price': '', 'unit_amount': '45'})

    # The trade is not saved to the database
    assert (Trade.objects.all().count() == 0)

    # The response code should be 200
    assert (response.status_code == 200)

    form = response.context['form']

    # Validation error msgs shown for unit price
    assert(
        'name="unit_price" min="0" class="slider numberinput form-control is-invalid' in str(form))

    # Validation error msgs not shown for unit amount
    assert not(
        'name="unit_amount" min="0" class="slider numberinput form-control is-invalid' in str(form))


# Test CurrentRoundView

def test_current_round_view_404_when_market_does_not_exists(client, db):
    url = reverse('market:current_round', args=('BARMARKETID',))
    response = client.get(url)
    assert (response.status_code == 404)


def test_response_status_code_200_when_market_exists(client, db):
    market = MarketFactory()
    url = reverse('market:current_round', args=(market.market_id,))
    response = client.get(url)
    assert (response.status_code == 200)

def test_returns_correct_non_zero_round(client, db):
    market = MarketFactory(round=11)
    url = reverse('market:current_round', args=(market.market_id,))
    response = client.get(url)
    assert (response.json() == {"round": 11})


# Test MyMarkets

def test_mymarkets_view_login_required(client, logged_in_user):
    """ user not logged in will be redirected to login page """
    client.logout()
    response = client.get(reverse('market:my_markets'))

    assert (response.status_code == 302)
    assert (response['Location'] ==
                     '/accounts/login/?next=/my_markets/')

def test_mymarkets_view_correct_template(client, logged_in_user):
    """ logged in user will see correct template """
    response = client.get(reverse('market:my_markets'))
    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/my_markets.html')

def test_mymarkets_view_no_markets_from_other_users(client, logged_in_user):
    """ User should not see markets created by other user """
    market = MarketFactory()  # some market created by anouther user
    response = client.get(reverse('market:my_markets'))
    assert (response.status_code == 200)
    assertContains(
        response, 'You have not yet created a market.')
    assertNotContains(response, market.market_id)

def test_mymarkets_view_user_has_created_a_market(client, logged_in_user):
    """ User has created a market so reponse should contain info on this market """
    market = MarketFactory(created_by=logged_in_user)
    response = client.get(reverse('market:my_markets'))
    assert (response.status_code == 200)
    assertNotContains(
        response, 'You have not yet created a market.')
    assertContains(response, market.market_id)


# Test TraderTable

## TODO!

# Test MarketEdit

###################### get requests ############################
def test_page_exits_and_uses_template(client, logged_in_user):
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    url = reverse('market:market_edit', args=(market.market_id,))

    response = client.get(url)

    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/market_edit.html')

def test_user_has_no_permission_to_edit_other_market(client, logged_in_user):
    """
    User only has permission to edit the markets she has created
    """
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    other_market_not_created_by_client = MarketFactory()

    url = reverse('market:market_edit', args=(
        other_market_not_created_by_client.market_id,))
    response = client.get(url)

    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:home'))

###################### post requests ############################

def test_valid_post_data_updates_market_and_redirects(client, logged_in_user):
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    data = {'product_name_singular': 'surdejsbolle',
            'product_name_plural': 'surdejsboller', 'alpha': 14, 'beta': 10, 'theta': 32,
            'endless' : True, 'initial_balance' : 53, 'max_rounds': 12,
            'min_cost': 35, 'max_cost': 3565}

    url = reverse('market:market_edit', args=(market.market_id,))
    response = client.post(url, data=data)

    market.refresh_from_db()
    assert (float(market.alpha) == 14)
    assert (market.product_name_singular == 'surdejsbolle')

    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))

def test_invalid_post_data_does_not_update_market(client, logged_in_user):
    """
    alpha is negative, so form is invalid. No values should be updated in this case
    """
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    client.login(username='somename', password='testpass123')

    data = {'product_name_singular': 'surdejsbolle',
            'product_name_plural': 'surdejsboller', 'alpha': -14, 'beta': 10, 'theta': 32,
            'endless' : True, 'initial_balance' : 53, 'max_rounds': 12,
            'min_cost': 35, 'max_cost': 3565}
    
    url = reverse('market:market_edit', args=(market.market_id,))
    response = client.post(url, data=data)

    market.refresh_from_db()
    # alpha has not changed
    assert (float(market.alpha) == 105.55)
    # product name has not changed
    assert (market.product_name_singular == 'baguette')
    assert (response.status_code == 200)  # return template
    assertTemplateUsed(response, 'market/market_edit.html')
