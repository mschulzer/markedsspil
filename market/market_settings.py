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
        "title": "Scenarie 1: Samme omkostninger",
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
        "title": "Scenarie 2: Forskellige omkostninger",
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
        "title": "Scenarie 3: Monopol / Ingen konkurrence",
        "description": mark_safe("En situation hvor forbrugerne slet ikke tager højde for forskellen mellem producentens pris og gennemsnitsprisen på markedet. Dvs. der er reelt ikke nogen konkurrence mellem producenterne, der i stedet fungerer som <b>monopol</b> på hver deres marked."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 0,
        "gamma": 3,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": "Scenarie 4: Hård konkurrence",
        "description": mark_safe("En situation hvor forbrugerne i meget høj grad tager højde for forskellen mellem producentens pris og gennemsnitsprisen på markedet. Dvs. en situation som er meget tæt på <b>fuldkommen konkurrence</b> mellem producenterne på markedet."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 97,
        "gamma": 3,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": "Scenarie 5: Stor prisfølsomhed",
        "description": mark_safe("En situation hvor forbrugernes efterspørgsel i meget høj grad afhænger af det prisniveau varen sælges til på markedet. Dvs. en vare med <b>høj priselasticitet</b> som f.eks. luksusvarer der godt kan undværes i tilfælde af en prisstigning."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 315,
        "theta": 14.5,
        "gamma": 20.5,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": "Scenarie 6: Lille prisfølsomhed",
        "description": mark_safe("En situation hvor forbrugernes efterspørgsel kun i meget ringe grad afhænger af det prisniveau varen sælges til på markedet. Dvs. en vare med <b>lav priselasticitet</b> som f.eks. essentielle varer der dårligt kan undværes selv ved en prisstigning.En situation hvor forbrugernes efterspørgsel i meget høj grad afhænger af det prisniveau varen sælges til på markedet. Dvs. en vare med høj priselasticitet som f.eks. luksusvarer der godt kan undværes i tilfælde af en prisstigning."),
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 75,
        "theta": 14.5,
        "gamma": 0.5,
        "min_cost": 8,
        "max_cost": 8,
        "max_rounds": 15,
        "endless": False,
        "allow_robots": False
    },
    {
        "title": "Scenarie 7: Brugerdefineret scenarie",
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
