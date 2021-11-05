{% load custom_tags %}
"""
Nedenfor definerer vi nogle brugbare konstanter, du kan anvende i din kode. Værdien af disse konstanter vil ændre sig fra runde til runde. 
""" 
# Din aktuelle saldo
balance = {{ trader.balance|to_float }}

# Din produktionsomkostning pr. enhed
prod_cost = {{ trader.prod_cost|to_float }}

# Det maksimale antal {{ market.product_name_plural }} du har råd til at producere
max_amount = {{ max_amount }}

# Den maksimale pris pr. {{ market.product_name_singular }} du kan vælge
max_price = {{ max_price|to_float }}

# Runde
round = {{ market.round|add:1 }}
{% if market.round > 0 %}
# Markedets gennemsnitspris i sidste rundend (vil være None i første runde)
avg_price = {{ round_stats.all.last.avg_price|to_float }}
{% else %}
# Markedets gennemsnitspris i sidste rundend (vil være None i første runnde)
avg_price = None
{% endif %}{% if market.round > 0 %}
# Efterspørgslen efter dine {{ market.product_name_plural }} i sidste runde (vil være None i første runde)
demand_last_round = {{ trades.last.demand }}
{% else %}
# Efterspørgslen efter dine {{ market.product_name_plural }} i sidste runde (vil være None i første runde)
demand_last_round = None{% endif %}
