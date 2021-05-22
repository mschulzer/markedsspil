# Create your tests here.
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ..models import Market
from django.core.exceptions import ValidationError

class JoinViewTest(SimpleTestCase):

    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/join.html'),

    def test_view_url_exists_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:join'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/join.html'),

    ## Test join med og uden Market id i session.

    ## Test join POST - med valid og invalid market_id

class CreateMarketViewTests(TestCase):

    # Test get requests
    def test_view_url_exists_at_proper_location_and_uses_proper_template(self):
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    def test_view_url_exits_at_proper_name_and_uses_proper_template(self):
        response = self.client.get(reverse('market:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'market/create.html'),

    # Test post requests
    def test_market_creation(self):
        # There should be 0 markets in db at this point
        self.assertEqual(Market.objects.all().count(), 0)
        response = self.client.post(
            reverse('market:create'), {'alpha': 21.402, 'beta': 44.2, 'theta': 2.0105, 'min_cost': 11, 'max_cost': 144})
        self.assertEqual(response.status_code, 302)

        # There should be 1 market in db at this point
        self.assertEqual(Market.objects.all().count(), 1)

        # New market has been created with proper values
        new_market = Market.objects.first()
        self.assertEqual(float(new_market.alpha), 21.402)
        self.assertEqual(float(new_market.beta), 44.2)
        self.assertEqual(float(new_market.theta), 2.0105)
        self.assertEqual(new_market.min_cost, 11)
        self.assertEqual(new_market.max_cost, 144)
        self.assertEqual(new_market.round, 0)
        self.assertEqual(len(new_market.market_id), 8)
        self.assertTrue(type(new_market.market_id) is str)
