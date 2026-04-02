"""
auth.py

This module handles authentication-related functionality for ThrivePay.

It provides utilities for hashing passwords, verifying passwords and creating JWT
tokens. We use passlib's bcrypt hashing scheme for storing passwords and
python-jose for signing and verifying JSON Web Tokens (JWT).

NOTE: For simplicity this example does not handle refresh tokens or token
revocation. In a production environment you should implement token
blacklisting or short-lived tokens with refresh tokens and proper
revocation lists.

Environment variables:
    SECRET_KEY: The secret key used to sign JWTs. You should generate a
        strong random string for this in production.
    ALGORITHM: The hashing algorithm to use for JWTs (default 'HS256').
    ACCESS_TOKEN_EXPIRE_MINUTES: Duration in minutes before an access token
        expires. Default is 60 minutes.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext


# Create a password hashing context. The bcrypt scheme is widely used and
# considered secure for password storage. Passlib will handle the salt
# internally and supports updating the hash when the scheme is upgraded.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default values for JWT
from os import getenv

SECRET_KEY = getenv("SECRET_KEY", "CHANGE_ME_SECRET")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: A dictionary of claims to include in the token payload. The
            dictionary is copied so the original input isn't modified.
        expires_delta: Optional timedelta specifying the token's expiry.

    Returns:
        A string representing the encoded JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode a JWT token and return the payload.

    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise exc
