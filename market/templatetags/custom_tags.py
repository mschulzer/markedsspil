from django import template
from django.utils.translation import gettext as _

register = template.Library()

def field_name_to_label(value):
    if value == "profit":
        value=_("Profit")
    elif value == "balance_after":
        value=_("Balance")
    elif value == "unit_price":
        value=_("Price per unit")
    elif value == "unit_amount":
        value=_("Unit amount")
    elif value == "demand":
        value=_("Demand")
    elif value == "units_sold":
        value=_("Units sold")
    elif value == "was_forced":
        value=_("Was forced")
    else:
        value="N/A"
    return value.title()

def get_attribute(value, arg): 

    if hasattr(value, str(arg)):
        attr = getattr(value, arg)
        if attr == None:
            return ' ---- '
        else:
            return attr

def subtract(value, arg):
    return value - arg
    
register.filter('field_name_to_label', field_name_to_label)
register.filter('get_attribute', get_attribute)
register.filter('subtract', subtract)
