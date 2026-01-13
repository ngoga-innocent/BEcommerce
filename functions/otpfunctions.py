import secrets
import hashlib

def generate_otp():
    return str(secrets.randbelow(1000000)).zfill(6)

def hash_otp(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()
