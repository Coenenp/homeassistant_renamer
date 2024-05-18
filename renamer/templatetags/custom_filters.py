import re
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def regex_replace(value, args):
    """Replaces all occurrences of the regex pattern in value with the replacement string."""
    try:
        search_regex, replace_regex = args.split(',')
        return re.sub(search_regex, replace_regex, value)
    except ValueError:
        # If there aren't exactly two values in args, return the original value
        return value
