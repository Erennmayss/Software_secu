import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


ENCRYPTED_PREFIX = 'enc::'


def _build_fernet_key() -> bytes:
    secret = settings.SECRET_KEY.encode('utf-8')
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    return Fernet(_build_fernet_key())


def encrypt_value(value: str | None) -> str:
    if value is None:
        return ''
    text = str(value)
    if not text:
        return ''
    if text.startswith(ENCRYPTED_PREFIX):
        return text
    token = get_fernet().encrypt(text.encode('utf-8')).decode('utf-8')
    return f'{ENCRYPTED_PREFIX}{token}'


def decrypt_value(value: str | None) -> str:
    if value is None:
        return ''
    text = str(value)
    if not text:
        return ''
    if not text.startswith(ENCRYPTED_PREFIX):
        return text
    token = text[len(ENCRYPTED_PREFIX):]
    try:
        return get_fernet().decrypt(token.encode('utf-8')).decode('utf-8')
    except (InvalidToken, ValueError):
        return ''
