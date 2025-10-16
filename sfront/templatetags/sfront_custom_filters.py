from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def duration_minutes(start_time, end_time):
    """Calcule la durée en minutes entre deux heures"""
    try:
        if start_time and end_time:
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration = end_minutes - start_minutes
            return max(0, duration)  # Éviter les durées négatives
        return 0
    except (AttributeError, TypeError):
        return 0

@register.filter
def get_unique_categories(faqs):
    """Retourne les catégories uniques des FAQ"""
    try:
        categories = set()
        for faq in faqs:
            if hasattr(faq, 'category') and faq.category:
                categories.add(faq.category)
        return sorted(list(categories))
    except (AttributeError, TypeError):
        return []
