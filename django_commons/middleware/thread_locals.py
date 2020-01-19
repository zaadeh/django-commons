# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from threading import local

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model


_thread_locals = local()


def get_current_request():
    """
    returns the request object for this thread
    """
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """
    returns the current user, if exist, otherwise returns None
    """
    request = get_current_request()
    if request:
        return getattr(request, 'user', None)
    else:
        return None


class TLSRequest(MiddlewareMixin):
    """
    Simple middleware that adds the request object in thread local storage.
    """

    def process_request(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "'{}' needs to be placed after django auth middleware".format(
                    self.__class__
                )
            )

        _thread_locals.request = request

    def process_response(self, request, response):
        """To avoid leaking thread local storage to next request"""
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    def process_exception(self, request, exception):
        """To avoid leaking thread local storage to next request"""
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
