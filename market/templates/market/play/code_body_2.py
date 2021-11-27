""" Du kan frit redigere i koden nedenfor """

import random, math

if round == 1:
    # I runde 1 foretager vi disse valg:
    price_choice = 2*prod_cost
    amount_choice = max_amount/4

else:
    # I senere runder:
    if profit_last_round > 0:
        # Hvis vi havde overskud, gør vi som i sidste runde:
        price_choice = price_last_round
        amount_choice = amount_last_round
    else:
        # Hvis vi havde underskud, prøver vi noget nyt:
        price_choice = random.uniform(0, max_price)
        amount_choice = random.randint(0, math.floor(max_amount/4))
