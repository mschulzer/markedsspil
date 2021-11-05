from django.utils.translation import gettext as _

# List of predefined market scenarios.
# Scenarios added to the list will get automatically shown as options in the create market interface.
# The first scenario in the list will be selected by default.

SCENARIOS = [
    {
        "title": _("Scenario 1: All traders have equal costs"),
        "description": _("In this scenario, all traders have the same unit production costs, so the traders compete on equal terms. This is a good place to start."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguettes",
        "initial_balance": 5000,
        "alpha": 105,
        "beta": 17.5,
        "theta": 14.5,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": _("Scenario 2: Some traders have an advantage"),
        "description": _("In this scenario, the traders are assigned different production costs at random, giving some traders an advantage over others."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguettes",
        "initial_balance": 5000,
        "alpha": 105,
        "beta": 17.5,
        "theta": 14.5,
        "min_cost": 5,
        "max_cost": 15,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False

    },
    {
        "title": _("Custom scenario"),
        "description": _("Create a market with parameters of your own choice."),
        "product_name_singular": "",
        "product_name_plural": "",
        "initial_balance": "",
        "alpha": "",
        "beta": "",
        "theta": "",
        "min_cost": "",
        "max_cost": "",
        "max_rounds": "",
        "endless": False,
        "allow_robots": False
    }
]
