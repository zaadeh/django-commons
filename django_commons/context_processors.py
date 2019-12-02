# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

from django.conf import settings
from django.utils import timezone


def current_datetime(request):
    """
    Returns the current date, time and timezone.
    """
    return {
        'current_datetime': timezone.now(),
        'current_datetime_local': timezone.localtime(),
        'current_timezone': timezone.get_current_timezone(),
        'current_timezone_name': timezone.get_current_timezone_name(),
    }


def settings_module(request):
    """
    Return the whole settings module in a dictionary in template context.

    Caution: This should be used very carefully to not cause security
    vulnerabilities.
    """
    return {
        'settings': {
            key: getattr(settings, key)
            for key in dir(settings)
            if not key.startswith('__') and key.isupper()
        }
    }
