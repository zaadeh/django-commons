# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

import jdatetime

from django import template

register = template.Library()


@register.filter
def jdtformat(value, fmt='%c', locale='fa_IR'):
    """
    Formats a date or time according to the given format.
    """
    dt = value
    if isinstance(value, datetime.datetime):
        dt = jdatetime.datetime.fromgregorian(datetime=value).aslocale(locale)
    elif isinstance(value, datetime.date):
        dt = jdatetime.date.fromgregorian(date=value)
    elif isinstance(value, jdatetime.datetime):
        pass
    else:
        raise NotImplementedError(
            'type "{}" not supported for jdformat filter'.format(type(value))
        )

    return dt.strftime(fmt)
