"""
Password hashing utilities.

We NEVER store raw passwords anywhere - only their hashed form.
This module provides two functions:
  - hash_password(): turn a plain password into a secure hash
  - verify_password(): check a plain password against a stored hash
"""

from passlib.context import CryptContext

# CryptContext manages which hashing algorithm(s) we use.
# "bcrypt" is a well-tested, deliberately slow (attack-resistant) algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Convert a plain-text password into a secure hash for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain-text password matches a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)