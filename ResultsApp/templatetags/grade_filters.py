from django import template

register = template.Library()

@register.filter
def grade_for_mark(mark, grades):
    for g in grades:
        if mark >= g.min_mark:
            return g.grade
    return ""
    

@register.filter
def comment_for_mark(mark, grades):
    for g in grades:
        if mark >= g.min_mark:
            return g.comment
    return ""

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)
