"""
List of predefined market scenarios.
Scenarios added to the list will get automatically shown as options in the create market interface.
The first scenario in the list will be selected by default.

Recall,
alpha is the basic demand
theta is the level of competition
gamma is the price sensitivity

"""
from django.utils.safestring import mark_safe


SCENARIOS = [
    {
        "title": "Standard baguettemarked",
        "description": "I dette scenarie, som forløber over 15 runder, er både prisfølsomhed og konkurrenceforhold tilstræbt normale, og alle producenter har samme produktionsomkostninger pr. baguette. Dette kan være et godt scenarie at begynde med.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 14.5,
        "gamma": 3.0,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg',
    },
    {
        "title": "Forskellige produktionsomkostninger",
        "description": "I dette scenarie tildeles producenterne forskellige produktionsomkostninger pr. baguette ved spillets start, hvilket giver nogle producenter en klar konkurrencefordel. Bortset fra det er situationen magen til scenarie 1.",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 14.5,
        "gamma": 3.0,
        "min_cost": 5,
        "max_cost": 15,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg',
    },
    {
        "title": "Monopol / Ingen konkurrence",
        "description": mark_safe("I dette scenarie tager forbrugerne slet ikke tager højde for forskellen mellem producentens pris og gennemsnitsprisen på markedet. Det vil sige, at der reelt ikke er nogen konkurrence mellem producenterne, der i stedet fungerer som <b>monopolister</b> på hver deres marked. Bortset fra det er situationen magen til scenarie 1."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 0,
        "gamma": 3,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg'
    },
    {
        "title": "Hård konkurrence",
        "description": mark_safe("I dette scenarie tager forbrugerne i meget høj grad tager højde for forskellen mellem producentens pris og gennemsnitsprisen på markedet. Vi er med andre ord tæt på <b>fuldkommen konkurrence</b> mellem producenterne på markedet. Bortset fra det er scenariet magen til scenarie 1."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 97,
        "gamma": 3,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg'
    },
    {
        "title": "Stor prisfølsomhed",
        "description": mark_safe("I dette scenarie afhænger forbrugernes efterspørgsel i meget høj grad afhænger af det prisniveau, varen sælges for på markedet. Baguetter er altså en vare med <b>høj priselasticitet</b>, hvilket normalt kendetegner f.eks. luksusvarer, der kan undværes i tilfælde af en prisstigning. Bortset fra det er situationen stort set magen til scenarie 1."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 315,
        "theta": 14.5,
        "gamma": 20.5,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg'
    },
    {
        "title": "Lille prisfølsomhed",
        "description": mark_safe("I dette scenarie afhænger forbrugernes efterspørgsel kun i meget ringe grad af det prisniveau, varen sælges for på markedet. Baguetter er med andre ord en vare med <b>lav priselasticitet</b>, hvilket normalt kendetegner f.eks. essentielle varer, der dårligt kan undværes selv ved en prisstigning. Bortset fra det er situationen stort set magen til scenarie 1."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 75,
        "theta": 14.5,
        "gamma": 0.5,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg'
    }
]
