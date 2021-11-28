""" Algoritme 2  - kan ikke redigeres """

import random, math

# I runde 1 foretager vi disse valg:
if round == 1:
    # Vi lader prisen pr. vare være dobbelt så 
    # stor som vores omkostning. pr. vare. 
    price_choice = 2 * prod_cost

    # Vi vælger at producere en femtedel af 
    # det maksimale antal vare, vi har råd til 
    # at producere. 
    amount_choice = max_amount / 5

# I senere runder går vi anderledes frem:
else:
    if profit_last_round > 0:
        # Hvis vi havde overskud, gør vi det samme som 
        # i sidste runde
        price_choice = price_last_round
        amount_choice = amount_last_round
    else:
        # Hvis vi ikke havde overskud, prøver vi noget nyt:

        # Vi vælger en tilfældig pris, som ligger et sted
        # mellem 100% og 150% af vores produktionsomkostning
        # pr. vare. 
        price_choice = random.uniform(prod_cost, 1.5 * prod_cost)

        # Vi vælger at producere et tilfældigt antal varer, 
        # som er mindst 0 varer og højest 1/5 af det maksimale
        # antal varer, vi har råd til at producere. 
        amount_choice = random.randint(0, math.floor(max_amount / 5))
