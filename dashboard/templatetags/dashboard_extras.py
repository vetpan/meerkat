from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Dictionary lookup filter for templates.
    Usage: {{ mydict|get_item:key }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)
