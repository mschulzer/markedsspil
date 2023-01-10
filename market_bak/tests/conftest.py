import pytest
from django.utils import translation
from .factories import UserFactory

@pytest.fixture(scope='function', autouse=True)
def english(settings):
    # Make sure english is the only choice (for situations where LocaleMiddleware is enabled)
    settings.LANGUAGE_CODE='en-US'
    settings.LANGUAGES=(('en', 'English'),)

    # Change language (for situations where LocaleMiddleware is disabled)
    translation.activate("en-US")

@pytest.fixture
def logged_in_user(db, client):
    user = UserFactory()
    client.login(username=user.username,
                 password='defaultpassword')
    return user
