# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import logging

import pytz

from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class TimezoneMiddleware(MiddlewareMixin):
    """
    This middleware is used to activate a particular timezone per request.

    timezone is selected according to a setting in request's session or
    a project-wide default.

    User could be allowed to select a timezone from a form and a view which
    processes the user-picked timezone.

    Other methods to select a suitable timezone for a request is to set it
    to the browser timezone detected by js. Detecting the location using the
    "Accept-Language" header or IP based geolocation are other possible
    sources which can help choose a timezone.
    """

    def process_request(self, request):
        if not hasattr(request, 'session'):
            logger.warn(
                'timezone middleware depends on request sessions. possible wrong middleware order?'
            )
            return

        tz_session_key = getattr(settings, 'TZ_SESSION_KEY', 'request_timezone')
        tz_name = request.session.get(tz_session_key)
        if tz_name:
            try:
                # sets the time zone for the current thread
                timezone.activate(pytz.timezone(tz_name))
                logger.debug(
                    'setting tz from session. current tz: "{}"'.format(
                        timezone.get_current_timezone()
                    )
                )
            except Exception as e:
                logger.exception(e)
        else:
            try:
                # activate the timezone set in django settings as a default
                timezone.activate(timezone.get_default_timezone())
                logger.debug(
                    'setting tz to default. current tz: "{}"'.format(
                        timezone.get_current_timezone()
                    )
                )
            except Exception as e:
                logger.exception(e)

    def process_response(self, request, response):
        # unsets the time zone for the current thread
        timezone.deactivate()
        return response
