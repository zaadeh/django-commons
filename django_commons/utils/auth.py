# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs
from django.shortcuts import resolve_url
from django.conf import settings
from django.utils.six.moves.urllib.parse import urlparse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
import six


logger = logging.getLogger(__name__)


def req_passes_test(
    test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, is_403=False
):
    """
    This decorator is mostly the same as `user_passes_test` decorator in
    Django, except instead of just `request.user` it makes the entire `request`
    object available to the test function.

    Optionally if test fails, return error code 403, instead of redirecting
    to login page.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            if is_403:
                raise PermissionDenied()
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            logger.debug(
                'redirecting to "{}", next "{}"'.format(resolved_login_url, path)
            )
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def req_permission_required(perm, **kwargs):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled.
    """
    return req_passes_test(lambda req: req.user.has_perm(perm), **kwargs)


def users_with_perm(perm_name, include_superusers=False, exclude_superusers=False):
    """
    Return a queryset with all users who have a particular permission.

    Permissions are queries either directly on the `User` object, or on
    any of groups they are a member of.

    `exclude_superusers` parameter could be useful to isolate permission
    problems.
    """
    assert isinstance(perm_name, six.string_types)
    assert not (
        include_superusers and exclude_superusers
    ), 'both actively including and excluding superusers is contradictory'

    if '.' in perm_name:
        app_label, code_name = perm_name.split('.', 2)
    else:
        app_label = None
        code_name = perm_name

    lookup = Q(user_permissions__codename=code_name) | Q(
        groups__permissions__codename=code_name
    )
    if app_label:
        lookup = (
            Q(user_permissions__codename=code_name)
            & Q(user_permissions__content_type__app_label=app_label)
        ) | (
            Q(groups__permissions__codename=code_name)
            & Q(groups__permissions__content_type__app_label=app_label)
        )

    if include_superusers:
        lookup = Q(is_superuser=True) | lookup
    elif exclude_superusers:
        lookup = Q(is_superuser=False) & lookup

    q = get_user_model().objects.filter(lookup)

    # return q.distinct()
    return q


def users_with_perms(
    perms, include_superusers=False, exclude_superusers=False, combine='intersection'
):
    """
    Return a queryset with union or intersection of all users with given permissions.

    Takes a list of permissions and returns either union or intersection of
    individual querysets that return users with a single permission.

    Make sure that the list of permissions is reasonably small, otherwise
    this can result in a very big query body being sent ot the db.
    """
    assert isinstance(perms, (list, tuple))
    assert combine in [
        'union',
        'intersection',
    ], 'either union or intersection must be set'

    if combine == 'union':
        q = get_user_model().objects.none()
    else:
        q = get_user_model().objects.all()

    for perm in perms:
        if combine == 'union':
            q = q.union(users_with_perm(perm, include_superusers, exclude_superusers))
        else:
            q = q.intersection(
                users_with_perm(perm, include_superusers, exclude_superusers)
            )
    return q
