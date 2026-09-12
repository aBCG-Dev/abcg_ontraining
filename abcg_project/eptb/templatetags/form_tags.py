from django import template

register = template.Library()


@register.filter
def getfield(form, field_name):
    return form[field_name]


@register.filter
def details_field(field):
    return field.form[f"{field.name}_details"]
