from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter
def dict_key(d, key):
    """Returns d[key] safely from a dict"""
    if not d:
        return None
    return d.get(key)

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a dictionary value using a variable key in templates"""
    return dictionary.get(key, 0)
