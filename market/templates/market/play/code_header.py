{% load custom_tags %}
"""
Below we define some useful constants that you can use in your script. The value of these constants will change from round to round.
""" 
# your current balance
balance = {{ trader.balance|to_float }}

# your production cost per unit (fixed)
prod_cost = {{ trader.prod_cost|to_float }}

# the maximal number of {{ market.product_name_plural }} you can afford to produce
max_amount = {{ max_amount }}

# the maximal price per {{ market.product_name_singular }} you can choose (fixed)
max_price = {{ max_price|to_float }}

# current round
round = {{ market.round|add:1 }}
{% if market.round > 0 %}
# market average price last round (will be None in first round)
avg_price = {{ round_stats.all.last.avg_price|to_float }}
{% else %}
# market average price last round (will be None in first round)
avg_price = None
{% endif %}{% if market.round > 0 %}
# demand for your {{ market.product_name_plural }} last round (will be None in first round)
demand_last_round = {{ trades.last.demand }}
{% else %}
# demand for your {{ market.product_name_plural }} last round (will be None in first round)
demand_last_round = None{% endif %}
