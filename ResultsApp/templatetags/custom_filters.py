from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key in a dictionary, or None if not found."""
    return dictionary.get(key)

@register.filter
def get(d, key):
    if d is None:
        return None
    return d.get(key)