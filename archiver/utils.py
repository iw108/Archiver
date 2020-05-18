
from binascii import hexlify
from hashlib import sha256

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_sha256_checksum(file_path):
    sha256_hash = sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            checksum = sha256_hash.hexdigest()
        return checksum
    except Exception:
        return None


def get_encryption_key(checksum, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=16, salt=salt,
        iterations=100000, backend=default_backend()
    )
    return hexlify(kdf.derive(checksum.encode('utf-8'))).decode('utf-8')
