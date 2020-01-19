from __future__ import unicode_literals, print_function, absolute_import

from django.core import checks, exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ['SerialField', 'SmallSerialField', 'BigSerialField']


def get_changes_between_objects(object1, object2, excludes=[]):
    """
    Finds the changes between the common fields on two model objects.
    Useful when we need to compare old and new instance of an object,
    for example in a pre_save signal receiver.

    :param object1: The first object
    :param object2: The second object
    :param excludes: A list of field names to exclude
    """
    changes = {}

    # For every field in the model
    for field in object1._meta.fields:
        # Don't process excluded fields or automatically updating fields
        if not field.name in excludes and not isinstance(field, fields.AutoField):
            # If the field isn't a related field (i.e. a foreign key)..
            if not isinstance(field, fields.related.RelatedField):
                old_val = field.value_from_object(object1)
                new_val = field.value_from_object(object2)
                # If the old value doesn't equal the new value, and they're
                # not both equivalent to null (i.e. None and "")
                if old_val != new_val and not (not old_val and not new_val):
                    changes[field.verbose_name] = (old_val, new_val)

            # If the field is a related field..
            elif isinstance(field, fields.related.RelatedField):
                if field.value_from_object(object1) != field.value_from_object(object2):
                    old_pk = field.value_from_object(object1)
                    try:
                        old_val = field.related.parent_model.objects.get(pk=old_pk)
                    except field.related.parent_model.DoesNotExist:
                        old_val = None

                    new_pk = field.value_from_object(object2)
                    try:
                        new_val = field.related.parent_model.objects.get(pk=new_pk)
                    except field.related.parent_model.DoesNotExist:
                        new_val = None

                    changes[field.verbose_name] = (old_val, new_val)

    return changes


class SerialField(models.IntegerField):
    """
    Django does not allow more than one `AutoField` on a model, because
    some DB backends can't handle that. Currently only PostgreSQL backend
    allows multiple `serial` fields as far as I'm aware.

    This model field enables adding extra auto-incrementing integer fields
    when using PostgreSQL as DB backend.

    Note: This actually will not work as a second auto-increment integer
    field in Django, because Django does not support omitting the value of
    a field in INSERT or UPDATE queries, since that would require an
    additional query by the ORM to fetch the value assigned to the field
    by the database.
    """

    description = _("PostgreSQL serial field")
    default_error_messages = {
        'unsupported_dbms': _("Current DBMS is not supported"),
    }

    def check(self, **kwargs):
        errors = super(SerialField, self).check(**kwargs)
        errors.extend(self._check_dbms(**kwargs))
        return errors

    def _check_dbms(self, **kwargs):
        return []
        # TODO: find the current model and its database engine.
        if connection.settings_dict['ENGINE'] not in [
            'django.db.backends.postgresql',
            'django.db.backends.postgresql_psycopg2',
        ]:
            return [
                checks.Error(
                    '{} can only be used with PostgreSQL'.format(
                        self.__class__.__name__
                    ),
                    obj=self,
                ),
            ]
        return []

    def check_dbms(self, connection):
        if connection.settings_dict['ENGINE'] not in [
            'django.db.backends.postgresql',
            'django.db.backends.postgresql_psycopg2',
        ]:
            raise exceptions.ImproperlyConfigured(
                '{} can only be used with PostgreSQL'.format(self.__class__.__name__)
            )

    def db_type(self, connection):
        self.check_dbms(connection)
        return 'serial'


class SmallSerialField(models.BigIntegerField, SerialField):
    def db_type(self, connection):
        self.check_dbms(connection)
        return 'smallserial'


class BigSerialField(models.BigIntegerField, SerialField):
    def db_type(self, connection):
        self.check_dbms(connection)
        return 'bigserial'
