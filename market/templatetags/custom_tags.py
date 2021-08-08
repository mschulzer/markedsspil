from django import template
from django.utils.translation import gettext as _

register = template.Library()

def field_name_to_label(value):
    if value == "profit":
        value=_("FieldName_Profit")
    elif value == "balance_after":
        value=_("FieldName_BalanceAfter")
    elif value == "unit_price":
        value=_("FieldName_UnitPrice")
    elif value == "unit_amount":
        value=_("FieldName_UnitAmount")
    elif value == "demand":
        value=_("FieldName_Demand")
    elif value == "units_sold":
        value=_("FieldName_UnitsSold")
    elif value == "was_forced":
        value=_("FieldName_WasForced")
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
