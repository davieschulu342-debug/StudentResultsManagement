from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Safely get an item from a dictionary in templates.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
