import base64
import os
from functools import lru_cache

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import settings


class PasswordManager:
    def __init__(self, master_password: str):
        self.master_password = master_password.encode()
        self.salt = os.urandom(16)
        self.backend = default_backend()

    def _derive_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=self.backend,
        )
        key = kdf.derive(self.master_password)
        return key

    def generate_hash(self, password: str):
        key = self._derive_key()
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(key), modes.CFB(iv), backend=self.backend
        )
        encryptor = cipher.encryptor()
        encrypted_password = (
            encryptor.update(password.encode()) + encryptor.finalize()
        )
        return base64.b64encode(self.salt + iv + encrypted_password).decode()

    def verify_password(self, password: str, hash_str: str):
        decoded_data = base64.b64decode(hash_str)
        salt = decoded_data[:16]
        iv = decoded_data[16:32]
        encrypted_password = decoded_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend,
        )
        key = kdf.derive(self.master_password)

        cipher = Cipher(
            algorithms.AES(key), modes.CFB(iv), backend=self.backend
        )
        decryptor = cipher.decryptor()
        decrypted_password = (
            decryptor.update(encrypted_password) + decryptor.finalize()
        )

        return password.encode() == decrypted_password


# Пример использования
# master_password = "your_master_password"
# manager = PasswordManager(master_password)

# password = "my_secure_password"
# hashed_password = manager.generate_hash(password)
# print("Hashed Password:", hashed_password)

# is_valid = manager.verify_password(password, hashed_password)
# print("Is valid:", is_valid)


@lru_cache()
def get_password_manager() -> PasswordManager:
    return PasswordManager(master_password=settings.SECRET_KEY)
