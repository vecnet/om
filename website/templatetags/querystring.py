# -*- coding: utf-8 -*-
#
# This file is part of the VecNet OpenMalaria Portal.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
