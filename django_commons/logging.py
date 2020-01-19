# -*- coding: utf-8 -*-
import logging.config  # needed when logging_config doesn't start with logging.config

from django.contrib.auth import get_user_model

from django_commons.middleware.thread_locals import (
    get_current_request,
    get_current_user,
)


class HttpRequestFilter(logging.Filter):
    """
    Attach the current django request object to the logging record.
    """

    def filter(self, record):
        current_request = get_current_request()
        if hasattr(record, 'request'):
            logger.warning(
                "Will not overwrite an existing request attribute on the logging record"
            )
            return True
        record.request = current_request
        return True


class HttpUserFilter(logging.Filter):
    """
    Attach the name of the currently logged in user to the logging record.

    When using Python logging module, if this filter is in effect, one
    can include "username" in the format string of a logger in logging
    configuration. If a user has been logged in using the
    "django.contrib.auth" app, the name will appear in the log record.

    This filter depends on the Python thread local storage and threaded
    execution of django to share the current user object between the modules
    implicitly. This solution makes some assumptions about how the
    application is run and so is considered hacky to a degree.

    If no user has logged in, the string "<anon>" will be attached.
    """

    def filter(self, record):
        logged_in_user = get_current_user()
        if hasattr(record, 'username'):
            logger.warning(
                "Will not overwrite an existing username attribute on the logging record"
            )
            return True
        if not logged_in_user:
            record.username = '<anon>'
        else:
            assert isinstance(logged_in_user, get_user_model())
            record.username = logged_in_user.username
        return True


class AMQPLogHandler(logging.Handler):
    """
    Push the logging record into an AMQP message broker.
    """

    # TODO
    pass
