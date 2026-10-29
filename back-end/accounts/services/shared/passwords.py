from functools import cache

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from accounts.models import UserCredential
from accounts.security import tokens


@cache
def dummy_password_hash():
    return make_password(tokens.new_secret())


def check_password_strength(password, user, field):
    try:
        validate_password(password, user)
    except DjangoValidationError as error:
        raise ValidationError({field: error.messages})


def replace_password(user, new_password, now):
    UserCredential.objects.filter(user=user).update(
        password_hash=make_password(new_password), password_changed_at=now, updated_at=now
    )
