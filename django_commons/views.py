from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytz
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def set_request_timezone(request):
    """
    Let the user explicitly select his timezone of choice for this website.

    This view should be used alongside TimezoneMiddleware, which depends
    on the timezone set in request's session to activate the timezone
    in Django.
    """
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        messages.success(request, _("timezone successfully set"))
        return redirect('/')
    else:
        timezones = pytz.common_timezones
        return render(request, 'timezone.html', locals())
