from django import template

register = template.Library()

@register.filter
def get_result(results_map, key_tuple):
    """
    Fetch result from results_map dictionary with key = (subject_id, term, test_type)
    Usage:
        student.results_map|get_result:subject.id,term,test_type
    """
    if not results_map:
        return None
    if isinstance(key_tuple, str):
        # Convert "subject_id|term|test_type" to tuple
        parts = key_tuple.split("|")
        if len(parts) == 3:
            subject_id, term, test_type = parts
            key = (int(subject_id), term, test_type)
            return results_map.get(key)
    return None
