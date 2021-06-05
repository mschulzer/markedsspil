from django import template

register = template.Library()

def field_name_to_label(value):
    if value == "balance_after":
        value= 'Balance'
    else: 
        value = value.replace('_', ' ')
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
