# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from django import forms
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def is_request_for_form(request, form):
    """
    Return true if the request includes all of the required or at least
    one of the non-required fields from the given form in GET parameters.
    This is useful when we have a view which optionally processes one
    or more submitted forms with the GET method and we want to be able
    to distinguish whether the view should process normally (as if no
    form is submitted) or process one of the forms.
    """

    assert isinstance(request, HttpRequest)
    assert isinstance(form, (forms.Form, forms.ModelForm))
    required_fields = [field for field in form.fields if form.fields[field].required]
    optional_fields = [
        field for field in form.fields if not form.fields[field].required
    ]
    if required_fields and all([field in request.GET for field in required_fields]):
        return True
    if any([field in request.GET for field in optional_fields]):
        return True
    return False
