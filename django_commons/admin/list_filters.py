"""
Taken from:
https://medium.com/@hakibenita/how-to-add-a-text-filter-to-django-admin-5d1db93772d8
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.db.models import Q
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class InputFilter(admin.SimpleListFilter):
    """
    This class, if listed in `ModelAdmin.list_filter` allows custom
    filtering logic and presentation in admin's side panel.

    See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter

    A class inheriting from django.contrib.admin.SimpleListFilter, which you
    need to provide the title and parameter_name attributes to and override
    the lookups and queryset methods.
    """

    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class UserFilter(InputFilter):
    parameter_name = 'user'
    title = _("User")

    def queryset(self, request, queryset):
        term = self.value()

        if term is None:
            return

        any_name = Q()
        for bit in term.split():
            any_name &= Q(user__first_name__icontains=bit) | Q(
                user__last_name__icontains=bit
            )

        return queryset.filter(any_name)
