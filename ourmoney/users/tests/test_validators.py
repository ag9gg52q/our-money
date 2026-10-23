import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.validators import MinimumLengthValidator


def test_short_password_message_is_in_romanian():
    validator = MinimumLengthValidator(min_length=8)

    with pytest.raises(ValidationError) as error:
        validator.validate('abc')

    assert error.value.messages == [
        'Parola este prea scurtă. Trebuie să conțină cel puțin 8 caractere.'
    ]
    assert error.value.code == 'password_too_short'


def test_long_enough_password_passes():
    MinimumLengthValidator(min_length=8).validate('12345678')


def test_validator_is_used_by_settings():
    with pytest.raises(ValidationError) as error:
        validate_password('Ab1!')

    assert 'Parola este prea scurtă. Trebuie să conțină cel puțin 8 caractere.' in (
        error.value.messages
    )
