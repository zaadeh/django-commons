# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.utils.deprecation import MiddlewareMixin


class ForceDefaultLanguageMiddleware(MiddlewareMixin):
    """
    Ignore `Accept-Language` HTTP headers.

    This will force Django I18N machinery to always choose
    settings.LANGUAGE_CODE as the default initial language, unless another
    one is set via sessions or cookies.

    Should be installed *before* any middleware that checks
    `request.META['HTTP_ACCEPT_LANGUAGE']`, namely
    `django.middleware.locale.LocaleMiddleware`.
    """

    def process_request(self, request):
        if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']
