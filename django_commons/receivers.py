# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

from django.core.signals import (request_started, request_finished,
    got_request_exception)
from django.db.backends.signals import connection_created
from django.db.models.signals import (pre_save, post_save, pre_delete,
    post_delete)
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import get_user_profile_model


logger = logging.getLogger(__name__)


#@receiver(connection_created)
def setup_db_connection(connection, **kwargs):
    """
    Perform per-connection setup like settings connection parameters.
    """
    logger.debug('setting up the database connection')
    if connection.vendor == 'postgresql':
        # set a timeout for statements
        with connection.cursor() as cursor:
            sql = "SET statement_timeout = '1h'"
            cursor.execute(sql)


#@receiver([post_save], sender=get_user_model(),
#    dispatch_uid='ensure_call_once__save_user_profile')
def save_user_profile(sender, **kwargs):
    """keep UserPorfile and auth.User models in sync
    """
    inst = kwargs['instance']
    defaults = {
        # optional list of user profile fields dependent on user fields
        # 'username': inst.username
    }
    obj, is_created = get_user_profile_model().objects.get_or_create(user=inst,
        **defaults)
    if kwargs.get('created', False):
        if is_created:
            logger.debug('user profile created: "{}"'.format(obj))
        else:
            logger.warning('user profile already exists: "{}"'.format(obj))

    obj.save()


#@receiver([post_delete], sender=get_user_model(),
#    dispatch_uid='ensure_call_once__delete_user_profile')
def delete_user_profile(sender, **kwargs):
    inst = kwargs['instance']
    obj, is_created = get_user_profile_model().objects.get_or_create(user=inst)
    if is_created:
        logger.warning('user profile was not already present: "{}"'.format(obj))
    obj.delete()
    logger.debug('user profile deleted: "{}"'.format(obj))

