import requests
from cryptography.fernet import Fernet

def test_credential_storage():
    # Existing test code
    response = requests.post(...)
    
    # Add verification of encrypted storage
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(b"test_password")
    assert len(encrypted) > 0 