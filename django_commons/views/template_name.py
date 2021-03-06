"""
Taken from https://github.com/phpdude/django-template-names
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re

# any char followed by a proper-cased word
_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
# any lower letter or number followed by a capital letter
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def get_app_template_folder(module, depth=1):
    """Returns file location of the app template folder."""
    m = module.split('.')
    if not m:
        return ''

    if m[-1] == 'views':
        m.pop(-1)

    return "/".join(m[-depth:]).lower()


def camel_to_snake(s):
    # turns camelCaseStringExample into camel_CaseString_Example
    # re.sub will process non-overlapping matches, so it won't find
    # the CaseString split during this substitution
    subbed = _underscorer1.sub(r'\1_\2', s)

    # turns camel_CaseString_Example into camel_Case_String_Example
    subbed2 = _underscorer2.sub(r'\1_\2', subbed)

    # turns camel_Case_String_Example into camel_case_string_example
    return subbed2.lower()


class TemplateNames(object):
    """Django view mixin class to generate a tuple of template names
    when template_name is not already set."""

    template_name = None
    app_path_depth = 1

    def get_template_exts(self):
        """Returns a list of template file extensions."""
        return ['html', 'jinja']

    def get_template_names(self):
        """Returns an iterable of template names: List if template_name is set,
        Tuple of "module/template.extension" if generated by this mixin."""
        if not getattr(self, 'template_name', None):
            return self._generate_normalized_template_names()

        return [self.template_name]

    def _generate_normalized_template_names(self):
        """Creates and returns tuple of template names."""
        module = get_app_template_folder(self.__module__, depth=self.app_path_depth)
        template = camel_to_snake(self.__class__.__name__)

        return tuple(
            "%s/%s.%s" % (module, template, ext) for ext in self.get_template_exts()
        )
