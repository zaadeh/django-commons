from __future__ import unicode_literals, print_function, absolute_import

import logging

from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

import pytz


logger = logging.getLogger(__name__)


def set_request_timezone(request):
    """
    Let the use explicitly select his timezone of choice for this website.
    This view should be used alongside TimezoneMiddleware, which depends on the
    timezone set in request's session to activate the timezone in django.
    """
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        messages.success(request, _('timezone successfully set'))
        return redirect('/')
    else:
        timezones = pytz.common_timezones
        return render(request, 'timezone.html', locals())
