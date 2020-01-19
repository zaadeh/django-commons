from __future__ import unicode_literals, print_function, absolute_import

from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import rotate_token


class CSRFRotateToken(MiddlewareMixin):
    """
    Create a new CSRF token cookie on each request
    """

    def process_response(self, request, response):
        rotate_token(request)
        return response
