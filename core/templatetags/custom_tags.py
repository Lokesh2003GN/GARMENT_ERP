from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
    
@register.filter
def unique_thari(pavu_map):
    seen = set()
    unique = []
    for pavu in pavu_map.values():
        if pavu.thari not in seen:
            seen.add(pavu.thari)
            unique.append(pavu.thari)
    return unique