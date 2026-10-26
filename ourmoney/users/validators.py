from django.contrib.auth.password_validation import (
    MinimumLengthValidator as DjangoMinimumLengthValidator,
)
from django.core.exceptions import ValidationError


class MinimumLengthValidator(DjangoMinimumLengthValidator):
    """Regula Django de lungime minimă, cu mesajele în română.

    Traducerea română inclusă în Django nu conține acest mesaj, așa că îl definim aici.
    """

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                'Parola este prea scurtă. '
                f'Trebuie să conțină cel puțin {self.min_length} caractere.',
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return f'Parola trebuie să conțină cel puțin {self.min_length} caractere.'
