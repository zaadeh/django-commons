# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging


logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Try various attributes of the request in order to get the real IP address
    of client.
    """

    ipaddr = request.META.get('HTTP_X_REAL_IP')
    if ipaddr is None:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ipaddr = x_forwarded_for.split(',')[0]
        else:
            ipaddr = request.META.get('REMOTE_ADDR')
    return ipaddr
