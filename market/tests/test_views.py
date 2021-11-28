"""
To run all tests:
$ make test

To run all tests in this file:
$ make test_views

To run only one or some tests:
docker-compose -f docker-compose.dev.yml run web pytest -k <substring of test function names to run>
"""
from django.test import TestCase
from django.urls import reverse
from ..models import Market, Trader, Trade, RoundStat, UnusedCosts
from ..forms import TraderForm
from decimal import Decimal
from .factories import TradeFactory, UnProcessedTradeFactory, ForcedTradeFactory, TraderFactory, UserFactory, MarketFactory
from ..scenarios import SCENARIOS

import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains

# Test home view


def test_home_view_url_exists_at_proper_location_and_uses_proper_template(client):
    response = client.get('/')
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/home.html')
    assert isinstance(response.context['form'], TraderForm)


def test_home_view_context_form_when_market_id_is_in_GET(client):
    response = client.get(
        reverse('market:home') + "?market_id=KXZCVCZL")
    assert response.status_code == 200
    assert isinstance(response.context['form'], TraderForm)
    assertContains(response, "KXZCVCZL")


def test_home_view_name_and_template(client):
    response = client.get(reverse('market:home'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/home.html')


def test_home_view_notify_users_who_have_already_joined_a_market(client, db):
    market = MarketFactory()
    trader = TraderFactory()

    session = client.session
    session['trader_id'] = trader.id
    session['market_id'] = market.market_id
    session['username'] = 'Alberte'
    session.save()

    response = client.get(reverse('market:home'))

    # user should somehow be informed that he has already joined the market with this id
    assertContains(response, market.market_id)
    assertContains(response, "Alberte")


# Test join_market view

def test_join_market_view_proper_behavior_when_no_market_id_in_form(db, client):
    response = client.post(reverse('market:join_market'), {
        'username': 'Helle', 'market_id': ''})
    assert response.status_code == 200
    assert 'trader_id' not in client.session
    assertContains(response, "This field is required.")
    assert Trader.objects.all().count() == 0


def test_join_market_view_proper_behavior_when_no_username_in_form(db, client):
    response = client.post(reverse('market:join_market'), {
        'name': '', 'market_id': 'SOME_MARKET_ID'})
    assert response.status_code == 200
    assert not ('trader_id' in client.session)
    assertContains(response, "This field is required.")
    assert Trader.objects.all().count() == 0


def test_join_market_view_proper_behavior_when_no_market_with_posted_market_id(db, client):
    market_id_with_no_referent = 'BAD_MARKET_ID'
    response = client.post(reverse('market:join_market'), {
        'name': 'Hanne', 'market_id': market_id_with_no_referent})
    assert (response.status_code == 200)
    assert not ('trader_id' in client.session)
    assertContains(
        response, 'Der er intet marked med dette ID')
    assert (Trader.objects.all().count() == 0)


def test_join_market_view_proper_behaviour_and_nice_feedback_message_when_username_not_available(db, client):
    market = MarketFactory()
    TraderFactory(market=market, name="jonna")

    response = client.post(reverse('market:join_market'), {
        'name': 'jonna', 'market_id': market.market_id})
    assert (response.status_code == 200)
    assert not ('trader_id' in client.session)
    assertContains(
        response, 'Der er allerede en producent med dette navn')
    assert (Trader.objects.all().count() == 1)


def test_join_market_view_new_trader_created_when_form_is_valid(db, client):
    market = MarketFactory(min_cost=4, max_cost=4)
    response = client.post(reverse('market:join_market'), {
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


def test_join_market_view_new_trader_who_enters_game_late_created_with_forced_trades_in_previous_rounds(db, client):
    # a market is in round 3
    market = MarketFactory(round=3)

    # a players named Hanne tries to join the market (she is late)
    response = client.post(reverse('market:join_market'), {
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


# Test create_market View GET Request

def test_create_market_view_name_and_template(client, logged_in_user):
    response = client.get(reverse('market:create_market'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/create_market.html'),


def test_create_market_view_login_required(client, logged_in_user):
    """ User not logged in will be redirected to login page """
    client.logout()
    response = client.get(reverse('market:create_market'))
    assert response.status_code == 302
    assert response['Location'] == '/accounts/login/?next=/create_market/'


# Test create_market View POST Request
def test_create_market_details_view_valid_data(client, logged_in_user):
    """ 
    A market is created when posting valid data & logged in user is set as market's creator 
    After successfull creation, client is redirected to monitor page
    """
    response = client.post(
        reverse('market:create_market'), {'scenario_id': 3})
    assert Market.objects.all().count() == 1
    market = Market.objects.first()
    assert (market.created_by == logged_in_user)
    assert (market.gamma == SCENARIOS[3]['gamma'])
    assert (response.status_code == 302)
    assert(response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


# Test create_market_details View GET Request

def test_create_market_details_view_name_and_template(client, logged_in_user):
    response = client.get(
        reverse('market:create_market_details')+'?scenario_id=4')
    assert response.status_code == 200
    assertTemplateUsed(response, 'market/create_market_details.html')


def test_create_market_details_view_name_and_template_no(client, logged_in_user):
    """ Redirect if no scenario id id provided """
    response = client.get(reverse('market:create_market_details'))
    assert response.status_code == 302


def test_create_market_view_login_required(client, logged_in_user):
    """ User not logged in will be redirected to login page """
    client.logout()
    response = client.get(reverse('market:create_market_details'))
    assert response.status_code == 302
    assert response['Location'] == '/accounts/login/?next=/create_market_details/'



@pytest.fixture
def create_market_data():
    return {
        'product_name_singular': 'baguettes',
        'product_name_plural': 'baguettes',
        'initial_balance': 5000,
        'alpha': 21.4,
        'theta': 2.0,
        'gamma': 1.2,
        'min_cost': 11,
        'max_cost': 144,
        'cost_slope': 0,
        'max_rounds': 15,
        'endless': False,
        'scenario_title': 'Scenario Title'
    }


def test_create_market_is_created_when_data_is_valid(client, logged_in_user, create_market_data):
    """ 
    A market is created when posting valid data & logged in user is set as market's creator 
    Since min_cost < max_cost two new Unused costs are produced
    After successfull creation, client is redirected to monitor page
    """
    response = client.post(
        reverse('market:create_market_details'), create_market_data)
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


def test_create_market_when_min_costs_equals_max_cost_no_unused_costs_are_produced(client, logged_in_user, create_market_data):
    """ 
    A market is created when posting valid data & logged in user is set as market's creator 
    After successfull creation, client is redirected to monitor page. 
    Since min_cost == max_cost not Unused costs are produced
    """
    create_market_data['max_cost'] = 11

    response = client.post(
        reverse('market:create_market_details'), create_market_data)
    assert (Market.objects.all().count() == 1)
    market = Market.objects.first()
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))

    # min_cost is less than max_cost. Therefore two Unused costs should have been produced after creating the market
    unused_costs = UnusedCosts.objects.all()
    assert (unused_costs.count() == 0)


def test_create_market_no_market_is_created_when_min_cost_bigger_than_max_cost_and_error_mgs_is_generated(client, logged_in_user, create_market_data):
    """ data is invalid """
    create_market_data['min_cost'] = 200
    response = client.post(
        reverse('market:create_market_details'), create_market_data)
    assert response.status_code == 200
    assert Market.objects.all().count() == 0
    assertContains(
        response, "Den minimale omkostning kan ikke være større end den maksimale")


def test_create_market_no_market_is_created_when_alpha_not_defined_and_error_mgs_is_generated(client, logged_in_user, create_market_data):
    """ data is invalid """
    create_market_data['alpha'] = ''
    response = client.post(
        reverse('market:create_market_details'), create_market_data)
    assert response.status_code == 200
    assert Market.objects.all().count() == 0
    assertContains(response, "This field is required.")


def test_create_market_if_user_chooses_negative_min_cost_he_gets_a_good_feedback_message(client, logged_in_user, create_market_data):
    """ 
    In the model, min_cost and max_cost are set as positive integers. 
    If the users chooses negative value, this should not cast a database error, but a nice feedback message
    """
    create_market_data['min_cost'] = -11
    response = client.post(
        reverse('market:create_market_details'), create_market_data)
    assert response.status_code == 200
    assertContains(
        response, "Ensure this value is greater than or equal to 0.01.")


def test_create_market_if_user_chooses_negative_max_rounds_he_gets_a_good_error_message(client, logged_in_user, create_market_data):
    """ 
    Max_rounds must be an integer >= 1. 
    """
    create_market_data['max_rounds'] = -4
    response = client.post(
        reverse('market:create_market_details'), create_market_data)
    assert (response.status_code == 200)
    assertContains(response, "Antal runder kan ikke være mindre end 1")


# Test Monitor View

def test_monitor_view_url_exists_at_proper_name_and_uses_proper_template(client, db, logged_in_user):
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
    """ client who did not create the market does not have access to monitor view """
    market = MarketFactory(created_by=logged_in_user)
    client.logout()
    other_user = UserFactory(username="olebole")
    client.login(username=other_user.username,
                 password='defaultpassword')
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    # redirect as no access
    assert (response.status_code == 302)


def test_monitor_view_market_is_in_context(client, db, logged_in_user):
    market = MarketFactory(created_by=logged_in_user)
    response = client.get(
        reverse('market:monitor', args=(market.market_id,)))
    assert response.context['market'].market_id == market.market_id
    assert response.context['market'].round == 0


def test_monitor_view_bad_market_id_raises_404(client, db, logged_in_user):
    market = MarketFactory()
    response = client.get(
        reverse('market:monitor', args=('BAD_MARKET_ID',)))
    assert response.status_code == 404


# Test PlayViewGetRequest

def test_player_view_get_no_trader_id_in_session_redirects_to_home(client):
    # some client who has not joined tries to access the wait page
    response = client.get(reverse('market:play', args=('SOMEMARKETD',)))

    # he should be redirected to the home page
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:home'))


def test_player_view_get_if_no_errors_and_time_to_wait_return_play_template_with_wait_content(client, db):
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
    assertTemplateUsed(response, 'market/play/play.html'),
    assert (response.context.get('wait'))

    # there should now be a message saying that the user is waiting
    assertContains(response, "wait")

    # This is round 0, so no data from last round should be shown
    assertNotContains(
        response, 'Text with info about last round choices and results')

    # Template should not contain a submit button
    assertNotContains(response, 'submit')


def test_player_view_get_proper_behavior_in_round_4_when_user_has_made_trade_in_this_and_last_round(client, db):
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
    assertTemplateUsed(response, 'market/play/play.html'),
    assert not (response.context.get('wait'))

    # template should contain data from last round
    assertContains(response, "134.98")

    # template should contain a submit button
    assertContains(response, "submit")

    # template should not contain a link to the monitor view, since game is not over
    assertNotContains(response, f"/{market.market_id}/monitor")


def test_player_view_get_proper_behavior_in_round_4_when_user_has_made_trade_in_this_but_NOT_in_last_round(client, db):
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
    assertTemplateUsed(response, 'market/play/play.html'),

    # The player should know that he didn't trade last round
    assertContains(response, "Du handlede ikke i sidste runde.")

    # template should contain a submit button
    assertContains(response, "submit")

    # template should not contain a link to the monitor view, since game is not over
    assertNotContains(response, f"/{market.market_id}/monitor")


def test_player_view_get_form_attributes_are_set_correctly(client, db):
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

    # we expect the max input value of unit_price to be 4* market.max_current_prod_cost = 12
    assert ('max="12.00"' in str(form))
    assert not ('max="16.00"' in str(form))

    # we expect the max input value of unit_amount to be floor(trader.balance/trader.prod_cost) = floor(101/2) = 50.00
    assert ('max="50"' in str(form))
    assert ('max="53"' not in str(form))


def test_player_view_get_game_over_when_rounds_equal_max_round(client, db):
    """
    When game is over, the user should be notified about this
    """
    market = MarketFactory(round=4, max_rounds=4,
                           endless=False, game_over=True)

    # a user has joined properly
    trader = TraderFactory(market=market, balance=101, prod_cost=2)
    session = client.session
    session['trader_id'] = trader.pk
    session['username'] = 'Hans'
    session.save()

    # user goes to play url
    response = client.get(reverse('market:play', args=(market.market_id,)))

    # user is informed about the game state
    assertContains(response, "Spillet er slut")

    # the player interface does not contain a submit button
    assertNotContains(response, 'submit')

    # the player interface contains a link to the monitor view
    #assertContains(response, f"/{market.market_id}/monitor")


# Test Play View POST Requests

def test_player_view_post_market_id_not_found_redirects_to_home(client):
    # client tryes to go the play page without having joined a market
    response = client.post(
        reverse('market:play', args=('SOMEMARKETID',)))
    # client should be redirected to home page
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:home'))


def test_player_view_post_test_if_all_data_is_good_then_save_trade_and_redirect_to_play(client, db):
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


def test_player_view_post_error_message_to_user_when_invalid_form(client, db):
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
    assert 'This field is required.</li></ul><input type="text" name="unit_price"' in str(
        form)

    # Validation error msgs not shown for unit amount
    assert 'This field is required.</li></ul><input type="text" name="unit_amount"' not in str(
        form)


# Test Current Round View

def test_current_round_view_404_when_market_does_not_exists(client, db):
    url = reverse('market:current_round', args=('BARMARKETID',))
    response = client.get(url)
    assert (response.status_code == 404)


def test_current_round_view_response_status_code_200_when_market_exists(client, db):
    market = MarketFactory()
    url = reverse('market:current_round', args=(market.market_id,))
    response = client.get(url)
    assert (response.status_code == 200)


def test_current_round_view_returns_correct_non_zero_round(client, db):
    market = MarketFactory(round=11)
    url = reverse('market:current_round', args=(market.market_id,))
    response = client.get(url)
    assert (response.json() == {
            'round': 11,
            'num_active_traders': 0,
            'num_ready_traders': 0,
            'game_over': False
            })


# Test My Markets

def test_mymarkets_view_login_required(client, logged_in_user):
    """ user not logged in will be redirected to login p
    age """
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
        response, 'Du har ikke oprettet nogen markeder endnu.')
    assertNotContains(response, market.market_id)


def test_mymarkets_view_user_has_created_a_market(client, logged_in_user):
    """ User has created a market so reponse should contain info on this market """
    market = MarketFactory(created_by=logged_in_user)
    response = client.get(reverse('market:my_markets'))
    assert (response.status_code == 200)
    assertNotContains(
        response, 'You have not yet created a market.')
    assertContains(response, market.market_id)


def test_mymarket_gets_deleted_on_post_request(client, logged_in_user):
    """ Market with given ID gets 'deleted' on post request """
    market = MarketFactory(created_by=logged_in_user)
    assert market.deleted is False

    response = client.post(reverse('market:my_markets'), {
                           'delete_market_id': market.market_id})

    market.refresh_from_db()

    assert market.deleted is True
    assert (response.status_code == 302)


# Test MarketEdit

def test_market_edit_page_exits_and_uses_template(client, logged_in_user):
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    url = reverse('market:market_edit', args=(market.market_id,))

    response = client.get(url)

    assert (response.status_code == 200)
    assertTemplateUsed(response, 'market/market_edit.html')


def test_market_edit_user_has_no_permission_to_edit_other_market(client, logged_in_user):
    """
    You can't edit a market you did not create
    """
    market = MarketFactory()

    url = reverse('market:market_edit', args=(
        market.market_id,))
    response = client.get(url)

    assert market.created_by != client
    assert (response.status_code == 302)
    assert (response['Location'] == reverse('market:home'))


def test_market_edit_valid_post_data_updates_market_and_redirects(client, logged_in_user):
    market = MarketFactory(created_by=logged_in_user, alpha=105.55)
    data = {'product_name_singular': 'surdejsbolle',
            'product_name_plural': 'surdejsboller', 'alpha': 14, 'gamma': 3.4, 'theta': 32,
            'endless': True, 'initial_balance': 53, 'max_rounds': 12,
            'min_cost': 35, 'max_cost': 3565, 'cost_slope': 0}

    url = reverse('market:market_edit', args=(market.market_id,))
    response = client.post(url, data=data)

    market.refresh_from_db()
    assert (float(market.alpha) == 14)
    assert (market.product_name_singular == 'surdejsbolle')

    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


def test_market_edit_invalid_post_data_does_not_update_market(client, logged_in_user):
    """
    alpha is negative, so form is invalid. No values should be updated in this case
    """
    market = MarketFactory(created_by=logged_in_user, alpha=105.5)
    client.login(username='somename', password='testpass123')

    data = {'product_name_singular': 'surdejsbolle',
            'product_name_plural': 'surdejsboller', 'alpha': -14, 'gamma': 3.34, 'theta': 32,
            'endless': True, 'initial_balance': 53, 'max_rounds': 12,
            'min_cost': 35, 'max_cost': 3565}

    url = reverse('market:market_edit', args=(market.market_id,))
    response = client.post(url, data=data)

    market.refresh_from_db()
    # alpha has not changed
    assert (float(market.alpha) == 105.5)
    # product name has not changed
    assert (market.product_name_singular == 'baguette')
    assert (response.status_code == 200)  # return template
    assertTemplateUsed(response, 'market/market_edit.html')


def test_set_game_over_view(client, logged_in_user):
    market = MarketFactory(
        round=7, created_by=logged_in_user, monitor_auto_pilot=False)
    assert not market.game_over

    # the client tries to set the game state to game over
    url = reverse('market:set_game_over',
                  args=(market.market_id,))
    response = client.post(url)
    market.refresh_from_db()

    # market is now game_over
    assert market.game_over

    # redirect to monitor after succesful post-request
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


def test_toggle_monitor_auto_pilot_setting(client, logged_in_user):
    """ Post request with toggle_auto_pilot should change the market's auto_pilot setting """
    market = MarketFactory(
        round=7, created_by=logged_in_user, monitor_auto_pilot=False)

    # autopilot is false by default
    assert not market.monitor_auto_pilot

    # now we toggle the setting
    url = reverse('market:toggle_monitor_auto_pilot_setting',
                  args=(market.market_id,))
    client.post(url)
    market.refresh_from_db()

    # autopilot is now true
    assert market.monitor_auto_pilot

    # we toggle the setting again
    response = client.post(url)
    market.refresh_from_db()

    # auto pilot is now false
    assert market.monitor_auto_pilot is False

    # redirect to monitor after succesful post-request
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


def test_remove_trader_from_market_when_round_number_bigger_than_0(client, logged_in_user):
    """ Testing the remove trader functionality when round number bigger than 0"""
    market = MarketFactory(
        round=7, created_by=logged_in_user)
    trader = TraderFactory(market=market)

    # Trader is not removed by default
    assert trader.removed_from_market is False

    url = reverse('market:remove_trader_from_market')
    response = client.post(url, {'remove_trader_id': trader.id})
    trader.refresh_from_db()

    # Trader is now 'removed' from database (not actually deleted)
    assert trader.removed_from_market is True

    # Redirect to monitor view after database update
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


def test_remove_trader_from_market_in_round_0(client, logged_in_user):
    """ Testing the remove trader functionality in round 0"""
    market = MarketFactory(
        round=0, created_by=logged_in_user)
    trader = TraderFactory(market=market)

    num_traders_in_db = Trader.objects.all().count()
    assert num_traders_in_db == 1

    url = reverse('market:remove_trader_from_market')
    response = client.post(url, {'remove_trader_id': trader.id})

    # Trader is now deleted from database
    num_traders_in_db = Trader.objects.all().count()
    assert num_traders_in_db == 0

    # Redirect to monitor view after database update
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))


def test_declare_bankruptcy(client, db):
    """ Testing declare bankruptcy functionality """
    trader = TraderFactory()
    session = client.session
    session['trader_id'] = trader.id
    session.save()

    assert not trader.bankrupt

    url = reverse('market:declare_bankruptcy', args=(trader.id,))
    response = client.post(url)
    trader.refresh_from_db()

    assert trader.bankrupt

    # Redirect to monitor view after database update
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:play', args=(trader.market.market_id,)))


#  Test finish_round view

def test_finish_round_view_production_cost_positive_slope(client, db, logged_in_user):
    """ 
    1) At the end of a round, each trader's production cost is changed by the market's production cost slope 
    2) The slope should be added to the markets total change counter
    """
    market = MarketFactory(created_by=logged_in_user, cost_slope=Decimal('10.00'))
    trader = TraderFactory(market=market, prod_cost=Decimal('5.00'))
    trade = UnProcessedTradeFactory(round=0, trader=trader)

    url = reverse('market:finish_round', args=(market.market_id,))

    response = client.post(url)
    trader.refresh_from_db()
    market.refresh_from_db()
    trade = UnProcessedTradeFactory(round=1, trader=trader)

    assert (trader.prod_cost == 15.00)
    assert market.accum_cost_change == 10.00

    response = client.post(url)
    trader.refresh_from_db()
    market.refresh_from_db()
    assert (trader.prod_cost == 25.00)
    assert market.accum_cost_change == 20.00


def test_finish_round_view_production_cost_negative_slope(client, db, logged_in_user):
    """
    Negative cost slope reducees prod cost
    """
    market = MarketFactory(created_by=logged_in_user,
                           cost_slope=Decimal('-10.0'))
    trader = TraderFactory(market=market, prod_cost=Decimal('50.00'))
    trade = UnProcessedTradeFactory(round=0, trader=trader)

    url = reverse('market:finish_round', args=(market.market_id,))
    response = client.post(url)
    trader.refresh_from_db()
    market.refresh_from_db()

    assert (trader.prod_cost == 40.00)
    assert market.accum_cost_change == -10.00


def test_finish_round_view_production_cost_cannot_get_negative(client, db, logged_in_user):
    """
    Negative cost slope reducees prod cost
    """
    market = MarketFactory(created_by=logged_in_user,
                           cost_slope=Decimal('-10.00'))
    trader = TraderFactory(market=market, prod_cost=Decimal('5.00'))
    trade = UnProcessedTradeFactory(round=0, trader=trader)

    url = reverse('market:finish_round', args=(market.market_id,))
    response = client.post(url)
    trader.refresh_from_db()

    # trader's cost
    assert (trader.prod_cost == 5.00)



def test_finish_round_view_404_when_market_does_not_exists(client, logged_in_user):
    """ If market with given id does not exist, return 404 page """
    url = reverse('market:finish_round', args=('BADMARKETID',))
    response = client.post(url)
    assert (response.status_code == 404)


def test_finish_round_view_redirect_to_monitor_url_when_valid_arguments(client, logged_in_user):
    """ Redirect to monitor view after successful post-request """
    # At least one trade has to have been made this round before post-request
    market = MarketFactory(created_by=logged_in_user)
    trader = TraderFactory(market=market)
    trade = UnProcessedTradeFactory(round=0, trader=trader)
    assert trade.round == trade.trader.market.round

    url = reverse('market:finish_round', args=(trade.trader.market.market_id,))
    response = client.post(url)
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(trade.trader.market.market_id,)))


def test_finish_round_view_one_trader_has_made_one_trade_this_round(client, logged_in_user):

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
    response = client.post(
        reverse('market:finish_round', args=(trade.trader.market.market_id,)))
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(trade.trader.market.market_id,)))

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


def test_finish_round_view_created_forced_moves_for_inactive_player(client, logged_in_user):
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
    response = client.post(
        reverse('market:finish_round', args=(market.market_id,)))

    # Reponse codes and redict location looks good
    assert (response.status_code == 302)
    assert (response['Location'] == reverse(
        'market:monitor', args=(market.market_id,)))

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


class FinishRoundViewMultipleUserTest(TestCase):

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
            theta=2.0105,
            gamma=42.1895,
            round=1,
            created_by=self.user)

        # 5 players in the market
        self.christian = TraderFactory(name="christian", market=self.market)
        self.martin = TraderFactory(name="martin", market=self.market)
        self.nadja = TraderFactory(name="nadja", market=self.market)
        #self.jens = TraderFactory(name="jens", market=self.market)
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

        # The 4 traders have chosen amount and price for round 1 (profit and balance_after_not_calculated_yet)
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

        num_ready_traders = self.market.num_ready_traders()
        assert (num_ready_traders == 4)

    def test_correct_response_code_and_location_after_post_request(self):
        response = self.client.post(
            reverse('market:finish_round', args=(self.market.market_id,)))
        assert (response.status_code == 302)
        assert (response['Location'] == reverse(
            'market:monitor', args=(self.market.market_id,)))

    def test_balance_and_profit_of_trades_updates(self):
        assert (self.c1.balance_after is None)
        assert (self.m1.balance_after is None)
        assert (self.n1.balance_after is None)
        assert (self.k1.balance_after is None)

        assert (self.c1.profit is None)
        assert (self.m1.profit is None)
        assert (self.n1.profit is None)
        assert (self.k1.profit is None)

        url = reverse('market:finish_round', args=(self.market.market_id,))

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
        url = reverse('market:finish_round', args=(self.market.market_id,))
        response = self.client.post(url)
        assert (RoundStat.objects.filter(
            round=1, market=self.market).exists())
        r1stat = RoundStat.objects.get(round=1, market=self.market)
        assert (r1stat.avg_price == (9+11+11+17)/4)

    def test_market_is_in_round_2(self):
        self.market.refresh_from_db()
        assert (self.market.round == 1)
        url = reverse('market:finish_round', args=(self.market.market_id,))
        response = self.client.post(url)
        assert (response.status_code == 302)
        self.market.refresh_from_db()
        assert (self.market.round == 2)

    def test_correct_num_trades_in_db(self):
        num_trades = Trade.objects.all().count()
        assert (num_trades == 8)

    def test_removal_of_trader(self):
        assert(self.market.round == 1)
        # Nadja has currently two trades in the database
        assert(Trade.objects.filter(trader=self.nadja).count() == 2)

        # Market host decides to remove Nadja from market
        url = reverse('market:remove_trader_from_market')
        response = self.client.post(url, {'remove_trader_id': self.nadja.id})
        self.nadja.refresh_from_db()

        # Nadja has been flagged as 'removed'
        assert (self.nadja.removed_from_market == True)

        # Nadja now only has one trade in the database
        assert(Trade.objects.filter(trader=self.nadja).count() == 1)

        # Total number of trades is down to 7
        num_trades = Trade.objects.all().count()
        assert (num_trades == 7)

        # The number of ready traders should now be 3
        self.market.refresh_from_db()
        num_ready_traders = self.market.num_ready_traders()
        assert (num_ready_traders == 3)

        christians_balance_before_finish_round = self.christian.balance

        # The market host finishes the round
        url = reverse('market:finish_round', args=(self.market.market_id,))
        response = self.client.post(url)

        # We are now in round 2
        self.market.refresh_from_db()
        assert(self.market.round == 2)

        assert (RoundStat.objects.filter(
            round=1, market=self.market).exists())

        # Nadjas price should not be part of the average for round 1
        r1stat = RoundStat.objects.get(round=1, market=self.market)
        expected_avg_price = round((9+11+17)/3, 2)
        assert float(r1stat.avg_price) == expected_avg_price

        # Nadjas amount should not be part of the average amount round 1
        r1stat = RoundStat.objects.get(round=1, market=self.market)
        expected_avg_amount = round((150+200+31)/3, 2)
        assert float(r1stat.avg_amount) == expected_avg_amount

        # Nadjas balance after round 1 should not be part of the average balance after round 1
        self.nadja.refresh_from_db()
        self.kristian.refresh_from_db()
        self.christian.refresh_from_db()
        self.martin.refresh_from_db()
        expected_avg_balance_after = round((
            self.kristian.balance + self.christian.balance + self.martin.balance) / 3, 2)
        assert float(r1stat.avg_balance_after) == float(
            expected_avg_balance_after)

        # Nadjas stored 'forced trade' for round 1 should mostly consist of None-values.
        nadjas_trade = Trade.objects.filter(trader=self.nadja, round=1).first()
        assert(nadjas_trade.was_forced == True)
        assert(nadjas_trade.unit_price == None)
        assert(nadjas_trade.unit_amount == None)
        assert(nadjas_trade.balance_after == None)
        assert(nadjas_trade.profit == None)
        assert(nadjas_trade.demand == None)
        assert(nadjas_trade.round == 1)

        # Let's also check that Christians values have been calculated correctly
        christians_trade = Trade.objects.get(
            trader=self.christian, round=1)
        alpha, gamma, theta = float(self.market.alpha), float(
            self.market.gamma), float(self.market.theta)

        # Recall, Christian chose these values
        christians_unit_price = unit_price = 11
        christians_unit_amount = 150

        christians_expenses = self.christian.prod_cost * christians_unit_amount
        christians_raw_demand = alpha - (gamma + theta) * \
            christians_unit_price + theta * expected_avg_price
        christians_demand = max(0, round(christians_raw_demand))
        christians_units_sold = min(christians_demand, christians_unit_amount)
        christians_income = 11 * christians_units_sold
        christians_trade_profit = christians_income - christians_expenses
        christians_new_balance = christians_balance_before_finish_round + christians_trade_profit

        assert(christians_trade.was_forced == False)
        assert(christians_trade.unit_price == 11)
        assert(christians_trade.unit_amount == 150)
        assert(christians_trade.profit == christians_trade_profit)
        assert(christians_trade.demand == christians_demand)
        assert(christians_trade.round == 1)
        assert christians_trade.balance_after == christians_new_balance
