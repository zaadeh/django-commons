from django.db import models


class ValidateModelMixin(object):

    """Make :meth:`save` call :meth:`full_clean`.
    .. warning:
        This should be the left-most mixin/super-class of a model.
    Django models ``save`` method does not validate all fields
    (i.e. call ``full_clean``) before saving the instance.

    The problem with this approach is, if the call to save() comes from a
    model form, the ``full_clean`` would have already been called, and here
    is called again.

    Another problem with this approach is methods like ``update``,
    ``select_for_update``, ``bulk_create``, etc. completely bypass this,
    unless they are overridden too.
    """

    def save(self, *args, **kwargs):
        """Call :meth:`full_clean` before saving."""
        self.full_clean()
        super(ValidateModelMixin, self).save(*args, **kwargs)


def get_user_profile_model():
    """
    This function should return the user profile class dynamically.

    Assuming there is only one model class with a OneToOne relationship
    with Django's `User` model, this function tries to find and return it.
    Other models that need to have arelation to `User` model, should instead
    define the relationsship to user profile model. This provision has the
    added advantage that makes it easier to port the application to other
    web frameworks.

    This function should work like `django.contrib.auth.get_user_mode()`,
    except for finding the `UserProfile` or similar model.
    """
    # TODO
    pass
