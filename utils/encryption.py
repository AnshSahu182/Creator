from cryptography.fernet import Fernet
import os

fernet = Fernet(os.getenv("FERNET_KEY"))

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()


# from cryptography.fernet import Fernet
# print(Fernet.generate_key().decode())
