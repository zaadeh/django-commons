# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
import string

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class MinPerCharClassPasswordValidator(object):
    """
    A password validation class which can enforce a minimum number of
    characters in each of various classes of characters (digits,
    alphabetical, lowercase, uppercase, and special symbols). It can
    also optionally check that for characters in each character class,
    they differ from each other.
    """

    def __init__(
        self,
        min_digit=1,
        min_alpha=1,
        min_lowercase=1,
        min_uppercase=1,
        min_special=1,
        must_vary=False,
    ):
        self.min_digit = min_digit
        self.min_alpha = min_alpha
        self.min_lowercase = min_lowercase
        self.min_uppercase = min_uppercase
        self.min_special = min_special
        self.must_vary = must_vary
        try:
            if not any(
                int(getattr(self, attr))
                for attr in [
                    'min_digit',
                    'min_alpha',
                    'min_lowercase',
                    'min_uppercase',
                    'min_special',
                ]
            ):
                raise ImproperlyConfigured(
                    "At least one class of characters must be set to a positive integer"
                )
        except ValueError:
            logger.error("Only integer parameters are acceptable")
            raise

    def password_changed(self, password, user=None):
        """
        The password has changed.
        """
        pass

    def validate(self, password, user=None):
        digit_chars = [ch for ch in password if ch in string.digits]
        if self.must_vary:
            digit_chars = set(digit_chars)
        if len(digit_chars) < self.min_digit:
            self.raise_error()

        alpha_chars = [ch for ch in password if ch in string.ascii_letters]
        if self.must_vary:
            alpha_chars = set(alpha_chars)
        if len(alpha_chars) < self.min_alpha:
            self.raise_error()

        lowercase_chars = [ch for ch in password if ch in string.ascii_lowercase]
        if self.must_vary:
            lowercase_chars = set(lowercase_chars)
        if len(lowercase_chars) < self.min_lowercase:
            self.raise_error()

        uppercase_chars = [ch for ch in password if ch in string.ascii_uppercase]
        if self.must_vary:
            uppercase_chars = set(uppercase_chars)
        if len(uppercase_chars) < self.min_uppercase:
            self.raise_error()

        special_chars = [ch for ch in password if ch in string.punctuation]
        if self.must_vary:
            special_chars = set(special_chars)
        if len(special_chars) < self.min_special:
            self.raise_error()

    def get_help_text(self):
        return _(
            "Your password must include some of uppercase, lowercase, digits and special characters"
        )

    def raise_error(self):
        err_list = []

        if self.min_digit:
            err_list.append(
                "{} ".format(self.min_digit)
                + (_("distinct") + " " if self.must_vary and self.min_digit > 1 else "")
                + _("digit")
            )

        if self.min_alpha:
            err_list.append(
                "{} ".format(self.min_alpha)
                + (_("distinct") + " " if self.must_vary and self.min_alpha > 1 else "")
                + _("alphabetical")
            )

        if self.min_lowercase:
            err_list.append(
                "{} ".format(self.min_lowercase)
                + (
                    _("distinct") + " "
                    if self.must_vary and self.min_lowercase > 1
                    else ""
                )
                + _("lowercase")
            )

        if self.min_uppercase:
            err_list.append(
                "{} ".format(self.min_uppercase)
                + (
                    _("distinct") + " "
                    if self.must_vary and self.min_uppercase > 1
                    else ""
                )
                + _("uppercase")
            )

        if self.min_special:
            err_list.append(
                "{} ".format(self.min_special)
                + (
                    _("distinct") + " "
                    if self.must_vary and self.min_special > 1
                    else ""
                )
                + _("special")
            )

        err = _("Password must contain at least these characters:")
        raise ValidationError(err + " " + ", ".join(err_list))
