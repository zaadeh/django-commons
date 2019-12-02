# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
def hasattrib(value, arg):
    """
    returns a boolean indicating whether an object has a particular attribute
    usage: {{ obj|hasattrib:someattr }}
    """
    return hasattr(value, str(arg))


@register.filter
def getattrib(value, arg):
    """
    gets an attribute of an object dynamically from a string name
    usage: {{ obj|getattrib:someattr }}
    """
    is_int = True
    try:
        int(arg)
    except ValueError:
        is_int = False

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif is_int and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID
