from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import rotate_token


class CSRFRotate(MiddlewareMixin):
    """
    Create a new CSRF cookie on each request
    """
    def process_response(self, request, response):
        rotate_token(request)
        return response

