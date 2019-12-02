# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.conf import settings

import bleach


register = template.Library()


@register.filter(name='bleach')
@stringfilter
def bleach_value(value):
    """
    Call the Bleach library clean method with parameters set in django settings.

    Return the sanitized HTML content and mark it safe to avoid further
    scaping by django template engine.
    Input value is expected to be unicode.
    """

    params = {
        'tags': 'BLEACH_ALLOWED_TAGS',
        'attributes': 'BLEACH_ALLOWED_ATTRIBUTES',
        'styles': 'BLEACH_ALLOWED_STYLES',
        'protocols': 'BLEACH_ALLOWED_PROTOCOLS',
        'strip': 'BLEACH_STRIP_TAGS',
        'strip_comments': 'BLEACH_STRIP_COMMENTS',
    }
    bleach_params = {
        key: getattr(settings, val)
        for key, val in params.items()
        if hasattr(settings, val)
    }
    bleached_value = bleach.clean(value, **bleach_params)
    return mark_safe(bleached_value)


@register.filter
@stringfilter
def bleach_linkify(value):
    return bleach.linkify(value, parse_email=True)
