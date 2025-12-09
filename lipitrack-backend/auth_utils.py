from jose import jwt
import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

PBKDF2_ITERATIONS = 100_000
SALT_LENGTH = 16


def hash_password(password: str) -> str:
    """
    Returns a base64-encoded string containing salt+hash
    """
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = password

    salt = os.urandom(SALT_LENGTH)
    dk = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, PBKDF2_ITERATIONS)
    stored = salt + dk
    return base64.b64encode(stored).decode("ascii")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Decodes stored_hash, recomputes PBKDF2, and compares in constant time
    """
    try:
        if isinstance(plain_password, str):
            password_bytes = plain_password.encode("utf-8")
        else:
            password_bytes = plain_password

        data = base64.b64decode(stored_hash.encode("ascii"))
        salt = data[:SALT_LENGTH]
        original_dk = data[SALT_LENGTH:]
        new_dk = hashlib.pbkdf2_hmac(
            "sha256", password_bytes, salt, PBKDF2_ITERATIONS)
        return hmac.compare_digest(original_dk, new_dk)
    except Exception:
        # Any decoding/format issue => treat as invalid password
        return False


SECRET_KEY = os.environ.get("LIPITRACK_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    data: dict that will go inside the token (e.g. data = {"sub": user_id})
    """
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
