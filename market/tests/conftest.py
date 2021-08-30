import pytest
from django.utils import translation

# Use english for all functions
@pytest.fixture(scope='function', autouse=True)
def english():
    translation.activate("en-US")

