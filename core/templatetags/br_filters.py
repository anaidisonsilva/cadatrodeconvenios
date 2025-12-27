from django import template

register = template.Library()

@register.filter(name="brl")
def brl(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0,00"

    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s
