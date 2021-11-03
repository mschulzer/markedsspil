# List of predefined market scenarios.
# Scenarios added to the list will get automatically shown as options in the create market interface.
# The first scenario in the list will be selected by default.

SCENARIOS = [
    {
        "title": "Scenario 1: Konkurrence på lige vilkår",
        "description": "I dette scenarie har alle forhandlere samme produktionsomkostninger pr. enhed. Alle konkurrerer derfor på lige vilkår. Dette er et godt scenarie at begynde med.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
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
        "title": "Scenario 2: Nogle forhandlere har en fordel",
        "description": "I dette scenarie tildeles forhandlerne forskellige produktionsomkostninger pr. enhed ved spillets start, hvilket giver nogle en konkurrencefordel.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
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
        "title": "Brugerdefineret scenarie",
        "description": "Skab et marked med parametre, du vælger helt selv.",
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
