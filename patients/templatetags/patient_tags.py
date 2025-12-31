from django import template

register = template.Library()

@register.filter
def safe_username(user):
    """Безопасное получение username или full_name"""
    if user:
        return user.get_full_name() or user.username
    return "Не указан"

@register.filter
def safe_getattr(obj, attr_name, default="Не указан"):
    """Безопасное получение атрибута"""
    if hasattr(obj, attr_name):
        value = getattr(obj, attr_name)
        if callable(value):
            value = value()
        return value if value is not None else default
    return default