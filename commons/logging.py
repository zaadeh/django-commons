import logging.config  # needed when logging_config doesn't start with logging.config

from commons.middleware.thread_locals import get_current_user


class HttpRequestFilter(logging.Filter):
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

    If no user has logged in, the string "anon" will be attached.
    """

    def filter(self, record):
        logged_in_user = get_current_user()
        if not logged_in_user:
            record.username = 'anon'
        else:
            record.username = logged_in_user.username
        return True