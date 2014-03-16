from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown2

register = template.Library()

@register.filter(is_safe=True, name="markdown")
@stringfilter
def markdown(value):
    return mark_safe(markdown2.markdown(value, safe_mode=True))
