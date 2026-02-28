from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64


# =====================================================
# CRYPTO
# =====================================================

class Crypto:
    def __init__(self,password,salt,token):
        self.password = password
        self.salt = salt
        self.token = token

    def get_password(self):
        return self.password

    def get_salt(self):
        return self.salt

    def get_token(self):
        return self.token

    def set_salt(self):
        self.salt = os.urandom(21)
        return self.salt

    def set_token(self,token):
        self.token = token

    def set_password(self,password):
        self.password = password

    def generate_key(master_password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

    def encrypt(password, fernet):
        return fernet.encrypt(password.encode())

    def decrypt(token, fernet):
        return fernet.decrypt(token).decode()