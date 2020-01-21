from __future__ import absolute_import, division, print_function, unicode_literals

from django.middleware.csrf import rotate_token
from django.utils.deprecation import MiddlewareMixin


class CSRFRotateToken(MiddlewareMixin):
    """
    Create a new CSRF token cookie on each request
    """

    def process_response(self, request, response):
        rotate_token(request)
        return response
