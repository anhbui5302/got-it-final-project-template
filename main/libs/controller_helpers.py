import hmac
from hashlib import pbkdf2_hmac
from os import urandom


def generate_hashed_password_and_salt(plain):
    salt = urandom(8)
    plain = plain.encode("utf-8")
    return pbkdf2_hmac("sha256", plain, salt, 260000).hex(), salt.hex()


def check_hashed_password(hashed, salt, plain):
    salt = salt.encode("utf-8")
    plain = plain.encode("utf-8")
    hashed_plain = pbkdf2_hmac("sha256", plain, salt, 260000).hex()
    return hmac.compare_digest(hashed, hashed_plain)
