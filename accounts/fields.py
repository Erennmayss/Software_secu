from django.db import models

from .security import decrypt_value, encrypt_value


class EncryptedTextField(models.TextField):
    description = 'Text field encrypted at rest'

    def from_db_value(self, value, expression, connection):
        return decrypt_value(value)

    def to_python(self, value):
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            return decrypt_value(value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return ''
        return encrypt_value(str(value))
