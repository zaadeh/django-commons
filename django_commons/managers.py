# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models
from django.db.models.manager import EmptyManager
from django.db.models.query import EmptyQuerySet

from .middleware.thread_locals import get_current_user


def get_user_manager(**kwargs):
    class UserSubsetManager(models.Manager):
        """
        This manager class overrides the default queryset object to only
        return model instances which have a relation to the currently
        logged in user.

        If this custom manager is set as the default manager for a model,
        it has the very nice advantage that it works for related objects too.
        """

        use_in_migrations = False

        def __init__(self, **kwargs):
            # TODO: try to find the user relation model attribute dynamically
            try:
                self.user_rel = kwargs['user_rel']
            except KeyError:
                raise ImproperlyConfigured(
                    "'user_rel' parameter is required in {}".format(self.__class__)
                )
            self.exempt_superuser = kwargs.get('exempt_superuser', True)
            self.exempt_staff = kwargs.get('exempt_staff', False)
            self.exempt_perm = kwargs.get('exempt_perm', 'access_all_records')

            super(UserSubsetManager, self).__init__()

        def get_queryset(self):
            """
            Limit the quesryset to set of records with a relation to the
            current user.
            """

            # Beware that by relying on the implicit user, we are going
            # around MVC separation, by sharing the logged-in user object
            # among controller and model layers.
            current_user = get_current_user()

            if not current_user or not current_user.is_active:
                # return EmptyQuerySet()  # model attribute will be set to None
                return super(UserSubsetManager, self).get_queryset().none()
            if self.exempt_superuser and current_user.is_superuser:
                return super(UserSubsetManager, self).get_queryset()
            if self.exempt_staff and current_user.is_staff:
                return super(UserSubsetManager, self).get_queryset()
            if self.exempt_perm and current_user.has_perm(self.exempt_perm):
                return super(UserSubsetManager, self).get_queryset()

            filter_params = {self.user_rel: current_user}
            return super(UserSubsetManager, self).get_queryset().filter(**filter_params)

        def for_user(self, user=get_current_user()):
            """
            Return the subset of records belonging to the given user.

            This manager method can be explicitly called in views
            """
            filter_params = {self.user_rel: user}
            return super(UserSubsetManager, self).get_queryset().filter(**filter_params)

    return UserSubsetManager(**kwargs)
