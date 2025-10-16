from django import template
from collections import defaultdict

register = template.Library()

@register.filter
def group_permissions_by_app(permissions):
    """
    Groupe les permissions par application (content_type.app_label)
    """
    if not permissions:
        return {}
    
    grouped = defaultdict(list)
    for perm in permissions:
        app_label = perm.content_type.app_label
        grouped[app_label].append(perm)
    
    return dict(grouped)

@register.filter
def split_features(value, arg=','):
    """
    Divise une chaîne de caractères en liste d'équipements
    Usage: {{ room.features|split_features:"," }}
    """
    if not value:
        return []
    # Divise par virgule et nettoie chaque élément
    features = [feature.strip() for feature in value.split(arg) if feature.strip()]
    return features

@register.filter
def clean_feature(value):
    """
    Nettoie un équipement individuel
    Usage: {{ feature|clean_feature }}
    """
    if not value:
        return ''
    return value.strip()

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value
