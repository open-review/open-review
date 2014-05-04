from django import template

register = template.Library()

@register.filter()
def format_author(review):
    return "Anonymous" if review.anonymous else review.poster.full_name()
