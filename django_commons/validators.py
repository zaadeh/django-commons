# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging

import jsonschema
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext, ugettext_lazy as _

logger = logging.getLogger(__name__)


# validate a given string to be acceptable as an identifier
validate_identifier = validators.RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_-]{0,99}$')

# validate a given string to be acceptable as a phone number
validate_phone_number = validators.RegexValidator(r'^\+?[\d][\d-]{7,20}$')

JSON_VALIDATOR_CLASSES = {
    3: jsonschema.Draft3Validator,
    4: jsonschema.Draft4Validator,
    6: jsonschema.Draft6Validator,
    7: jsonschema.Draft7Validator,
}


def validate_jsonschema(schema, version=4):
    """
    Validate a JSON schema string, using a schema schema validator.

    JSON Schema versions 3, 4, 6 and 7 are supported.
    """
    try:
        validator_class = JSON_VALIDATOR_CLASSES[version]
    except KeyError:
        logger.warning("JSON schema version is invalid: '{}'".format(version))
        raise ValidationError(_("JSON schema version is invalid"))

    json_obj = schema
    if isinstance(json_obj, str):
        try:
            json_obj = json.loads(json_obj)
        except (ValueError, json.JSONDecodeError) as e:
            logger.debug("failed to load JSON schema document: '{}'".format(e))
            raise ValidationError(_("Failed to load JSON schema document"))

    try:
        validator_class.check_schema(json_obj)
    except jsonschema.SchemaError as e:
        logger.debug("failed to validate JSON schema document: '{}'".format(e))
        raise ValidationError(
            ' '.join((_("Failed to validate JSON schema document"), e.message))
        )


def validate_json(json_obj, schema=None, version=4):
    """
    Validate a JSON string.

    Optionally check against given JSON schema.
    """
    if isinstance(json_obj, str):
        try:
            json_obj = json.loads(json_obj)
        except (ValueError, json.JSONDecodeError) as e:
            logger.debug(
                "failed to load the string as valid JSON document: '{}'".format(e)
            )
            raise ValidationError(_("Failed to load the string as valid JSON document"))

    # TODO: implement different jsonschema versions
    if schema:
        try:
            jsonschema.validate(instance=json_obj, schema=schema)
        except jsonschema.ValidationError as e:
            logger.debug(
                "failed to validate JSON document against schema: '{}'".format(e)
            )
            raise ValidationError(
                ' '.join(
                    (_("Failed to validate JSON document against schema"), e.message)
                )
            )
        except jsonschema.SchemaError as e:
            logger.debug("failed to validate JSON schema document: '{}'".format(e))
            raise ValidationError(
                ' '.join((_("Failed to validate JSON schema document"), e.message))
            )


@deconstructible
class JSONSchemaValidator(object):
    """
    """

    message = _("Enter a valid JSON document")
    code = 'invalid'

    def __init__(self, *args, **kwargs):
        self._schema = kwargs['schema']
        self._version = int(kwargs.get('version', 4))
        try:
            self._validator_class = JSON_VALIDATOR_CLASSES[self._version]
        except KeyError:
            logger.warning("JSON schema version is invalid: '{}'".format(self._version))
            raise ValidationError(_("JSON schema version is invalid"))

        if isinstance(self._schema, str):
            try:
                self._schema = json.loads(self._schema)
            except (ValueError, json.JSONDecodeError) as e:
                logger.debug("failed to load JSON schema document: '{}'".format(e))
                raise ValidationError(_("Failed to load JSON schema document"))

    def __eq__(self, other):
        return (
            isinstance(other, JSONSchemaValidator)
            and self._schema == other._schema
            and self._version == other._version
            and (self.message == other.message)
            and (self.code == other.code)
        )

    def __ne__(self, other):
        return not (self == other)

    def __call__(self, value):
        """
        Validate that the given document passes JSON schema validation rules.
        """
        validate_json(value, self._schema)
