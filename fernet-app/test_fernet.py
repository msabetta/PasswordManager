from key_manager import get_fernet

fernet = get_fernet()

encrypted = fernet.encrypt(b"password123")
print("Cifrata:", encrypted)

decrypted = fernet.decrypt(encrypted)
print("Decifrata:", decrypted.decode())