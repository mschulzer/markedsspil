{% load custom_tags %}"""
Nedenfor definerer vi nogle brugbare konstanter,
du kan anvende i dit program. Værdien af disse
konstanter vil ændre sig fra runde til
runde. 

NB: Du kan ikke redigere i denne del af koden.
""" 

# Din aktuelle saldo:
balance = {{ trader.balance|to_float }}

# Din produktionsomkostning pr. enhed:
prod_cost = {{ trader.prod_cost|to_float }}

# Det maksimale antal {{ market.product_name_plural }} du har råd 
# til at producere:
max_amount = {{ max_amount }}

# Den maksimale pris pr. {{ market.product_name_singular }} du
# kan vælge:
max_price = {{ max_price|to_float }}

# Igangværende runde:
round = {{ market.round|add:1 }}
{% if market.round > 0 %}
# Din produktion i sidste runde:
amount_last_round = {{ trades.last.unit_amount }}
{% else %}
# Din produktion i sidste runde 
# (vil være None i første runnde):
amount_last_round = None
{% endif %} {% if market.round > 0 %}
# Din pris i sidste runde:
price_last_round = {{ trades.last.unit_price | to_float }}
{% else %}
# Din pris i sidste runde
# (vil være None i første runnde):
price_last_round = None
{% endif %}{% if market.round > 0 %}
# Markedets gennemsnitspris i sidste runde:
avg_price_last_round = {{ round_stats.all.last.avg_price | to_float }}
{% else %}
# Markedets gennemsnitspris i sidste runde
# (vil være None i første runde):
avg_price_last_round = None
{% endif %}{% if market.round > 0 %}
# Efterspørgslen på dine {{ market.product_name_plural }}
# i sidste runde:
demand_last_round = {{ trades.last.demand }}
{% else %}
# Efterspørgslen på dine {{ market.product_name_plural }} i sidste runde
#  (vil være None i første runde)
demand_last_round = None{% endif %}
