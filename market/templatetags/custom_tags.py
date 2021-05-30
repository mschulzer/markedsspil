from django import template

register = template.Library()

def field_name_to_label(value):
    value = value.replace('_', ' ')
    return value.title()

register.filter('field_name_to_label', field_name_to_label)
