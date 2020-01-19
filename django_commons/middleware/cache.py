from __future__ import unicode_literals, print_function, absolute_import

from django.utils.cache import add_never_cache_headers
from django.utils.deprecation import MiddlewareMixin


class DisableClientSideCachingMiddleware(MiddlewareMixin):
    """
    Adds headers to a response to indicate that a page should never be cached.

    This middleware can be used for testing and debugging cache issues
    in web browsers and intermediary web proxies.
    """

    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
