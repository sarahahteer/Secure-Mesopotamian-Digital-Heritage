
import secrets

from cryptography.fernet import Fernet
from flask import current_app


def get_cipher():
    key = current_app.config.get("FILE_ENCRYPTION_KEY")

    if not key:
        raise RuntimeError(
            "File encryption key is not configured."
        )

    if isinstance(key, str):
        key = key.encode("utf-8")

    try:
        return Fernet(key)
    except (TypeError, ValueError):
        raise RuntimeError(
            "File encryption key is invalid."
        )


def encrypt_file(file_data):
    if not file_data:
        raise ValueError("لا يمكن تشفير ملف فارغ.")

    return get_cipher().encrypt(file_data)


def decrypt_file(encrypted_data):
    if not encrypted_data:
        raise ValueError("البيانات المشفرة فارغة.")

    return get_cipher().decrypt(encrypted_data)


def generate_stored_filename():
    return secrets.token_hex(32) + ".enc"
