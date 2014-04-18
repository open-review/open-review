from django import template

register = template.Library()

@register.filter(is_safe=True, name="format_votes")
def format_votes(review):
    delta = review.n_upvotes - review.n_downvotes
    return (str(delta) if delta <= 0 else '+' + str(delta))
