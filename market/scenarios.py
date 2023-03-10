"""
List of predefined market scenarios.
Scenarios added to the list will get automatically shown as options in the create market interface.

Recall,
alpha is the basic demand
theta is the level of competition
gamma is the price sensitivity

"""
from django.utils.safestring import mark_safe


SCENARIOS = [
    {
        "title": "Standard baguettemarked",
        "description": "I dette scenarie, som forløber over 20 runder, er markedsparametrene indstillet så alle producenter på markedet har en god mulighed for at tjene nogle penge. Men de producenter som er bedst til at afstemme produktion og pris vil naturligvis tjene mest. (Dette er en god markedstype at vælge første gang man spiller Markedsspillet.)",
        "product_name_singular": "baguette",
        "product_name_plural": "baguetter",
        "initial_balance": 5000,
        "alpha": 105,
        "theta": 14.5,
        "gamma": 3.0,
        "min_cost": 8,
        "max_cost": 8,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/baguettes3.jpg',
    },
    {
        "title": "Småkageproducenter (med ulige forhold)",
        "description": "På dette marked har producenterne forskellige produktionsomkostninger, hvilket naturligvis giver nogle en fordel og andre en ulempe i konkurrencen på markedet. Markedstypen kan bruges til at illustrere, at på et frit marked vil de mest effektive producenter (dem med de laveste produktionsomkostninger) klare sig bedre end mindre effektive producenter.",
        "product_name_singular": "småkage",
        "product_name_plural": "småkager",
        "initial_balance": 5000,
        "alpha": 220,
        "theta": 20.0,
        "gamma": 4.3,
        "min_cost": 10,
        "max_cost": 18,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/cookies.jpg',
    },

    {
        "title": "Robust rugbrødsmarked",
        "description": "I udgangspunktet har producenterne rigtig gode forhold på dette marked. Det egner sig derfor til et længere spil hvor man undervejs i spillet øger udfordringen for deltagerne ved at redigere markedsindstillingerne. Man kan f.eks. sænke den grundlæggende efterspørgsel for at illustrere faldende efterspørgsel i en lavkonjunktur eller økonomisk krise. Man kunne også øge produktionsomkostningerne per enhed for at illustrere stigende råvarepriser.",
        "product_name_singular": "rugbrød",
        "product_name_plural": "rugbrød",
        "initial_balance": 5000,
        "alpha": 160,
        "theta": 13,
        "gamma": 2.3,
        "min_cost": 9,
        "max_cost": 9,
        "cost_slope": 0,
        "max_rounds": 40,
        "endless": False,
        "allow_robots": False,
        "img": 'img/rug.jpg',
    },
    {
        "title": "Klubtrøjer (monopollignende marked)",
        "description": mark_safe("Klubtrøjer, f.eks. fra forskellige fodboldklubber, er et eksempel på et marked hvor forbrugerne ofte har en meget stærk tilknytning til en specifik sportsklub og aldrig kunne drømme om at købe en klubtrøje fra en konkurrerende sportsklub. Klubberne har derfor nærmest monopol i forhold til at sælge trøjer til deres egne fans, hvilket resulterer i en markedspris som ligger langt over produktionsomkostningerne. (På dette marked kan man forestille sig at alle priser er angivet i 10 kr., dvs. en pris på 15 svarer til 150 kr.)"),
        "product_name_singular": "klubtrøje",
        "product_name_plural": "klubtrøjer",
        "initial_balance": 5000,
        "alpha": 180,
        "theta": 2.0,
        "gamma": 5.0,
        "min_cost": 10,
        "max_cost": 10,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/jersies.jpg'
    },
    {
        "title": "Soyabønner (konkurrencepræget marked)",
        "description": mark_safe("Råvarer, som f.eks. soyabønner, hvede, ris og lignende er ofte markeder hvor produkterne er relativt ensartede (homogene) og hvor der er mange producenter. På et sådant marked vil konkurrencen mellem producenterne være meget hård (tæt på fuldkommen konkurrence), hvilket resulterer i en markedspris som bliver presset næsten helt ned mod produktionsomkostningerne. (Markedstype 4 og 5 har samme grundindstillinger på nær konkurrenceforholdene.)"),
        "product_name_singular": "sæk med soyabønner",
        "product_name_plural": "sække med soyabønner",
        "initial_balance": 5000,
        "alpha": 180,
        "theta": 100.0,
        "gamma": 5.0,
        "min_cost": 10,
        "max_cost": 10,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/soybeans.jpg'
    },
    {
        "title": "Designer-sneakers (luksusvare)",
        "description": mark_safe("Luksusvarer, som f.eks. designer-sneakers, er varer som mange forbrugere eftertragter, men som samtidig er noget som godt kan undværes hvis prisen er for høj. Dette betyder at markeder for luksusvarer ofte er relativt prisfølsomme, dvs. at den samlede efterspørgsel efter varen i høj grad afhænger af prisen. (På dette marked kan man forestille sig at alle priser er angivet i 1000 kr., dvs. en pris på 15 svarer til 15.000 kr.)"),
        "product_name_singular": "designer-sneakers",
        "product_name_plural": "designer-sneakers",
        "initial_balance": 5000,
        "alpha": 150,
        "theta": 15.0,
        "gamma": 10.0,
        "min_cost": 10,
        "max_cost": 10,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/sneaks.jpg'
    },
    {
        "title": "Madolie (basisvare)",
        "description": mark_safe("Basisvarer, som f.eks. madolie, er varer som er en grundlæggende del af husholdningen hos mange forbrugere, og som de vil have svært ved at undvære selv hvis prisen stiger. Dette betyder at markeder for basissvarer ofte ikke er særligt prisfølsomme, dvs. at den samlede efterspørgsel efter varen kun i begrænset omfang afhænger af prisen. (Markedstype 6 og 7 har samme grundindstillinger på nær prisfølsomheden.)"),
        "product_name_singular": "liter madolie",
        "product_name_plural": "liter madolie",
        "initial_balance": 5000,
        "alpha": 150,
        "theta": 15.0,
        "gamma": 1.0,
        "min_cost": 10,
        "max_cost": 10,
        "cost_slope": 0,
        "max_rounds": 20,
        "endless": False,
        "allow_robots": False,
        "img": 'img/oil.jpg'
    }
]
