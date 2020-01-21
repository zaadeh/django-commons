# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging

import pytz

from django.utils import timezone

logger = logging.getLogger(__name__)


def in_active_timezone(value, noexp=False):
    """
    Given a `datetime.datetime` object, return an aware datetime object in the
    currently active Django timezone.

    This function can optionally block exceptions for invalid datetime
    values, and try it's best to return a meaningful result. This is to be
    used as a last resort, when dealing with incomplete and ambiguous
    datetime objects.
    """
    assert isinstance(value, datetime.datetime)

    result = value
    tz_active = timezone.get_current_timezone()
    tz_default = timezone.get_default_timezone()
    if timezone.is_naive(value):
        try:
            result = timezone.make_aware(value)
        except pytz.exceptions.AmbiguousTimeError:
            # At the end of a DST transition period, a particular wallclock time will
            # occur twice (once before the clocks are set back, once after). Both
            # possibilities may be correct, unless further information is supplied.
            if not noexp:
                raise
            else:
                logger.warning(
                    "a naive datetime with ambiguous value received: '{}'".format(value)
                )
                # One correction strategy is to always assume a fixed value
                # of True or False for is_dst.
                # Another strategy is to assume that the datetime value has
                # been generated in a place with the same timezone as currently
                # active timezone, and we are hopefully close enough to the
                # moment that this datetime value has been generated that
                # current DST status applies to it too.
                now = timezone.make_naive(timezone.localtime())
                is_dst = tz_active.dst(now) != datetime.timedelta(0)
                result = timezone.make_aware(value, is_dst=is_dst)
        except pytz.exceptions.NonExistentTimeError:
            # At the start of a DST transition period, the wallclock time jumps forward.
            # The instants jumped over never occur.
            if not noexp:
                raise
            else:
                logger.warning(
                    "a naive datetime with non-existent value received: '{}'".format(
                        value
                    )
                )
                # Here we assume that transition to DST has resulted in the
                # wall clock to jump forward, but for whatever reason the
                # system wall clock has failed to follow. So we let pytz
                # add the amount of DST offset to the given value, hoping this
                # "corrected" value does actually exist.
                result = timezone.make_aware(value, is_dst=True)
        except pytz.exceptions.InvalidTimeError as e:
            # Unknown cause for invalid datetime value
            logger.error("Unable to process datetime value: '{}'".format(e))
            raise
    else:
        tz_name_active = timezone.get_current_timezone_name()
        tz_name_default = timezone.get_default_timezone_name()
        if tz_active != tz_default:
            logger.debug(
                "current tz '{}' differs from default '{}'".format(
                    tz_name_active, tz_name_default
                )
            )
        if value.tzinfo == tz_active:
            logger.debug(
                "the value is already in the current timezone '{}' : '{}'".format(
                    value.tzinfo, tz_active
                )
            )
        result = timezone.localtime(value)
    return result
