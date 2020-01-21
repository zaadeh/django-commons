# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Add or update URL query parameters.

    The purpose of this tag is to help add or update one or more of url query
    parameters, without losing the rest of parameters. One common use is for
    updating pagination parameters in the url for a search page, which
    usually depends on GET method to carry the state.

    Should only be used on the part after the `?` on url string, not on the
    whole url.

    This tag requires `django.template.context_processors.request` context
    processor to be enabled.

    Because the query parameters are put into a dict before being re-encoded,
    their order is lost.
    """

    query = context['request'].GET.copy()
    for key in kwargs.keys():
        if key in query:
            # to avoid multiple value for a key
            del query[key]
    query.update(kwargs)
    return query.urlencode()
