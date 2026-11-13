"""Secure file primitives. Integrate ClamAV scanning before releasing files."""
import os
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf"}

def encrypt_file(data: bytes, key: bytes):
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 16, 24, or 32 bytes")
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, data, None)

def decrypt_file(ciphertext: bytes, key: bytes, nonce: bytes):
    return AESGCM(key).decrypt(nonce, ciphertext, None)

def safe_storage_name(original_name: str):
    cleaned = secure_filename(original_name)
    suffix = Path(cleaned).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("امتداد الملف غير مسموح")
    return f"{uuid4().hex}{suffix}.enc"
