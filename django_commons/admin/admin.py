# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models


class NoDeleteModelAdmin(admin.ModelAdmin):
    """
    This `ModelAdmin` subclass tries to remove the `delete` link and action.

    Even users who have been granted `app.delete_model` permission can not
    delete the record.

    This is useful for models in which the entities are synchronized
    externally, for example using signals. One use case could be `UserProfile`
    models which have a one to one relationship with Django `User` model and
    are created and deleted at the same time as `User` objects via signals.
    """

    def get_actions(self, request):
        # disable delete action
        actions = super(NoDeleteModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """Disable delete button."""
        return False


class NoAddModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        """Disable add button."""
        return False


class NoChangeModelAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        """Disable changes in admin."""
        return False


class AssignUserModelAdmin(admin.ModelAdmin):
    """
    Assign the current logged-in user object to the current saving object.

    This class can find the field on the current model which is related to
    the Django `User` and assign the current logged-in user in admin interface
    to this field on `save()`.
    """

    def save_model(self, request, obj, form, change):
        """To assign the current logged-in user to the creator_user field
        """
        # TODO: find the actual user relation field name
        # for field in obj._meta.fields:
        # if isinstance(field, models.fields.related.RelatedField)
        # models.field.value_from_object(obj)

        if not change or not obj.creator_user:
            user = get_user_model().objects.get(username=request.user.username)
            obj.creator_user = user
        return super(admin.ModelAdmin, self).save_model(request, obj, form, change)
