import secrets
import hashlib
from pydantic import SecretStr


"""server key"""
SERVER_KEY = secrets.token_bytes(32)  # binary data


def generate_token() -> SecretStr:
    return secrets.token_urlsafe(32)


def hash_token(token: SecretStr) -> :
    token = token.get_secret_value()
    return hashlib.blake2b(
        token.encode("utf-8"), key=SERVER_KEY, digest_size=32
    ).hexdigest()
