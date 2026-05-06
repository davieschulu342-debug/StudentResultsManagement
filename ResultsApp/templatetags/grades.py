from django import template

register = template.Library()

# Grade 12 ECZ system
@register.filter
def grade12(score):
    if score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"

# Grade 9 ECZ system
@register.filter
def grade9(score):
    if score >= 75:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"

# Grade 7 ECZ system
@register.filter
def grade7(score):
    if score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"
    
    # Example ECZ grading
GRADING = {
    "SENIOR": [(80, 'A'), (70, 'B'), (60, 'C'), (50, 'D'), (0, 'F')],
    "JUNIOR": [(75, 'A'), (65, 'B'), (50, 'C'), (40, 'D'), (0, 'F')],
    "UPPER_PRIMARY": [(70, 'A'), (60, 'B'), (50, 'C'), (40, 'D'), (0, 'F')],
    "LOWER_PRIMARY": [(70, 'A'), (60, 'B'), (50, 'C'), (40, 'D'), (0, 'F')],
    "ECE": [(70, 'A'), (60, 'B'), (50, 'C'), (40, 'D'), (0, 'F')],
}

@register.filter
def grade(score, level):
    try:
        score = float(score)
    except:
        return ''
    for min_score, g in GRADING.get(level, GRADING["ECE"]):
        if score >= min_score:
            return g
    return ''
