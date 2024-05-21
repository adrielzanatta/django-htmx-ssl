from django import template


register = template.Library()


@register.filter(name="key")
def get_dict_value(value, arg):
    return value.get(arg, 0)


@register.filter(name="abs")
def get_abs_value(value):
    return abs(value)


@register.filter
def team_side(value, arg):
    return value.filter(team__side_name=arg)
