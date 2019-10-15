from __future__ import unicode_literals, print_function, absolute_import

from django.core import checks, exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ['SerialField', 'SmallSerialField', 'BigSerialField']


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
                'django.db.backends.postgresql_psycopg2']:
            return [
                checks.Error(
                    '{} can only be used with PostgreSQL'.format(self.__class__.__name__),
                    obj=self
                ),
            ]
        return []

    def check_dbms(self, connection):
        if connection.settings_dict['ENGINE'] not in [
                'django.db.backends.postgresql',
                'django.db.backends.postgresql_psycopg2']:
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
