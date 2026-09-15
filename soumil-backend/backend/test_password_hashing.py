"""
Manual test for password hashing.
"""

from app.auth.security import hash_password, verify_password

plain = "MySecret123"

hashed = hash_password(plain)
print("Original password:", plain)
print("Hashed password:  ", hashed)

# Correct password should verify True
print("Correct password matches:", verify_password(plain, hashed))

# Wrong password should verify False
print("Wrong password matches:  ", verify_password("WrongPassword", hashed))