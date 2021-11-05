# List of predefined market scenarios.
# Scenarios added to the list will get automatically shown as options in the create market interface.
# The first scenario in the list will be selected by default.

SCENARIOS = [
    {
        "title": "Scenario 1: Konkurrence på lige vilkår",
        "description": "I dette scenarie har alle producenter de samme produktionsomkostninger pr. enhed. Alle konkurrerer derfor på lige vilkår. Dette er et godt scenarie at begynde med.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 14.5,
        "gamma": 3.0,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": "Scenario 2: Nogle producenter har en fordel",
        "description": "I dette scenarie tildeles producenterne tilfældigt forskellige produktionsomkostninger ved spillets start, hvilket giver nogle producenter en klar konkurrencefordel.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 14.5,
        "gamma": 3.0,
        "min_cost": 5,
        "max_cost": 15,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False

    },
    {
        "title": "Brugerdefineret scenarie",
        "description": "Opret et marked med dine egne indstilliger.",
        "product_name_singular": "",
        "product_name_plural": "",
        "initial_balance": "",
        "alpha": "",
        "theta": "",
        "gamma": "",
        "min_cost": "",
        "max_cost": "",
        "max_rounds": "",
        "endless": False,
        "allow_robots": False
    }
]
