# Copyright (C) 2015, University of Notre Dame
# All rights reserved
from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def query_string_replace(context, field, value):
    """ This template tag will replace specified parameter in Query String.
    Original: http://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
    Created specifically for pagination in ListView

    Examples: if Query String was page=1&sort_by=occupation
    {% url_replace "page" "3" %} will produce page=3&sort_by=occupation

    :param context: Template context
    :param field: field in query string
    :param value: new value for that field
    :return: new query string
    :rtype: str
    """

    request = context['request']
    query_string = request.GET.copy()

    query_string[field] = value

    return query_string.urlencode()
