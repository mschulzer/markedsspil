from django.utils.translation import gettext as _

# List of predefined market scenarios.
# Scenarios added to the list will get automatically shown as options in the create market interface.
# The first scenario in the list will be selected by default.

SCENARIOS = [
    {
        "description": _("Scenario 1. All traders have the same production costs. This is a good place to start."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguettes",
        "initial_balance": 5000,
        "alpha": 105,
        "beta": 17.5,
        "theta": 14.58,
        "min_cost": 8,
        "max_cost": 8,
    },
    {
        "description": _("Scenario 2. Traders are assigned different production costs at random, giving some traders an advantage over others."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguettes",
        "initial_balance": 5000,
        "alpha": 105,
        "beta": 17.5,
        "theta": 14.58,
        "min_cost": 5,
        "max_cost": 15
    },
    {
        "description": _("Custom scenario. Create a market with parameters of your choice."),
        "product_name_singular": "",
        "product_name_plural": "",
        "initial_balance": "",
        "alpha": "",
        "beta": "",
        "theta": "",
        "min_cost": "",
        "max_cost": ""
    }
]
