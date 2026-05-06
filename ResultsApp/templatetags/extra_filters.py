from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Returns d[key] safely from a dict"""
    if not d:
        return None
    return d.get(key)
