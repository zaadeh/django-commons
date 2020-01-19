from __future__ import absolute_import, print_function, unicode_literals

import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """json encoder that can handle `Decimal` type

    Usage:

        d = Decimal('42.5')
        json.dumps(d, cls=DecimalEncoder)

    Django includes a more complete JSON encoder at
    `django.core.serializers.DjangoJSONEncoder` that in addition to decimals,
    can handle `date`, `time`, `datetime`, `UUID`, etc.
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
