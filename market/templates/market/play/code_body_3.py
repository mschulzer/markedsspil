""" Algoritme 3  - kan ikke redigeres """

# I runde 1 foretager vi disse valg:
if round == 1:
  price_choice = prod_cost + 2
  amount_choice = max_amount/2

# I senere runder:
else:
  price_choice = avg_price_last_round + 3
  amount_choice = demand_last_round

# Forstår du algoritmen? Tror du, at den  
# vil give overskud i det lange løb?