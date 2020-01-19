# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import sys
import json

from django.core import exceptions
from django.core.management import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import force_str
from django.utils.text import capfirst
from django.utils import timezone
from django.contrib.auth.management import get_default_username
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


class NotRunningInTTYException(Exception):
    pass


class Command(BaseCommand):
    """This command is used to create or update a user object
    """

    help = "Create a user, optionally in bulk mode, showing a status report"
    missing_args_message = "Enter at least a username."
    requires_migrations_checks = True

    start_time = None
    required_user_params = {'username', 'password'}
    all_user_params = {
        'username',
        'password',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined',
        'groups',
        'permissions',
    }

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(
            self.UserModel.USERNAME_FIELD
        )

    def execute(self, *args, **options):
        self.start_time = timezone.localtime()
        retval = super(Command, self).execute(*args, **options)
        if options['verbosity'] > 1:
            self.stdout.write(
                self.style.WARNING(
                    "started at {}, took {}".format(
                        self.start_time, timezone.localtime() - self.start_time
                    )
                )
            )
        return retval

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            action='store',
            dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )
        parser.add_argument(
            '--file',
            '--file',
            action='store',
            dest='file_name',
            default=False,
            help='read user data from a file',
        )
        parser.add_argument(
            '--update_existing',
            '--update_existing',
            action='store_true',
            dest='update_existing',
            default=False,
            help=('Update existing user'),
        )
        parser.add_argument(
            '--{}'.format(self.UserModel.USERNAME_FIELD),
            dest=self.UserModel.USERNAME_FIELD,
            help='Specifies the login for the user.',
        )
        parser.add_argument(
            '--password', default=None, help='Specifies the password for the user.',
        )
        for param in Command.all_user_params - Command.required_user_params:
            parser.add_argument(
                '--{}'.format(param),
                default=None,
                help='Specifies the {} for the user'.format(param),
            )

    def upsert_user(self, user_params, update_existing=False):
        assert Command.required_user_params <= set(user_params.keys())
        assert set(user_params.keys()) <= Command.all_user_params

        user_params_cleaned = {}

        try:
            for field_name in user_params:
                field = self.UserModel._meta.get_field(field_name)
                user_params_cleaned[field_name] = field.clean(
                    user_params[field_name], None
                )
        except exceptions.ValidationError as e:
            raise CommandError("'{}': {}".format(field_name, '; '.join(e.messages)))

        try:
            user = get_user_model().objects.get_by_natural_key(
                username=user_params_cleaned['username']
            )

            if not update_existing:
                raise CommandError("user already exists")

            if 'password' in user_params_cleaned:
                try:
                    validate_password(user_params_cleaned['password'], user)
                except exceptions.ValidationError as e:
                    raise CommandError(
                        "'{}': {}".format(
                            user_params_cleaned['username'], '; '.join(e.messages)
                        )
                    )
                user.set_password(user_params_cleaned['password'])
            else:
                user.set_unusable_password()

            for attr in set(user_params_cleaned.keys()) - {
                'username',
                'password',
                'groups',
                'permissions',
            }:
                setattr(user, attr, user_params_cleaned[attr])

            self.stdout.write(
                "updating user '{}'... ".format(user_params_cleaned['username']),
                ending='',
            )
            user.save()
        except get_user_model().DoesNotExist:
            try:
                validate_password(user_params_cleaned['password'])
            except exceptions.ValidationError as e:
                raise CommandError(
                    "'{}': {}".format(
                        user_params_cleaned['username'], '; '.join(e.messages)
                    )
                )

            params = {
                key: user_params_cleaned[key]
                for key in set(user_params_cleaned.keys()) - {'groups', 'permissions'}
            }
            user = get_user_model().objects.create_user(**params)
            # user = get_user_model().objects.create_superuser('foo', email='', password='')
            self.stdout.write(
                "creating user '{}'... ".format(user_params_cleaned['username']),
                ending='',
            )
            user.save()
        except get_user_model().MultipleObjectsReturned as e:
            raise CommandError(e)

        # user.groups.add([Group.objects.get_or_create(name=group_name)[1]  for group_name in []])
        # user.user_permissions.add([Permission.objects.get_or_create(content_type='', codename='')[1] for perm in []])

        self.stdout.write(self.style.SUCCESS('successful'))

    def handle(self, *args, **options):
        # database = options['database']
        file_name = options['file_name']
        update_existing = options['update_existing']

        if file_name:
            self.stdout.write(
                "Creating users in bulk mode using data from '{}'".format(file_name)
            )
            try:
                file_data = json.loads(open(file_name).read())
                # TODO: validate json using an schema
            except (ValueError, IOError) as e:
                raise CommandError('\n'.join(e.messages))

            for item in file_data:
                self.upsert_user(user_params=item, update_existing=update_existing)
        else:
            username = options[self.UserModel.USERNAME_FIELD]
            password = options.get('password')

            user_params = {
                'username': username,
                'password': password,
            }
            for param in Command.all_user_params - Command.required_user_params:
                if options[param]:
                    user_params[param] = options[param]

            self.upsert_user(user_params=user_params, update_existing=update_existing)
