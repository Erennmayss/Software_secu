import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    def validate(self, password, user=None):
        errors = []
        if len(password or '') < 8:
            errors.append(_('Le mot de passe doit contenir au moins 8 caracteres.'))
        if not re.search(r'[A-Z]', password or ''):
            errors.append(_('Le mot de passe doit contenir au moins une lettre majuscule.'))
        if not re.search(r'\d', password or ''):
            errors.append(_('Le mot de passe doit contenir au moins un chiffre.'))
        if not re.search(r'[^A-Za-z0-9]', password or ''):
            errors.append(_('Le mot de passe doit contenir au moins un caractere special.'))
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            'Votre mot de passe doit contenir au moins 8 caracteres, une majuscule, un chiffre et un caractere special.'
        )
