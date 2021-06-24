
scenarios = [
    {
        "description": "Scenario 1. All traders have the same production costs. This is a good place to start.",
        "id": "scenario_1", 
        "checked": True, # Chosen by default in radio button input group
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
        "description": "Scenario 2. Traders have different production costs and competition is uneven.",
        "id": "scenario_2",
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
        "description": "Custom. Feel free to create your own market!",
        "id": "custom",
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
