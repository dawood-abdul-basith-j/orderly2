import hashlib
import os
import base64
import hmac
from typing import Tuple

def derive_pbkdf2(password: str, salt: bytes = None, iterations: int = 390000) -> Tuple[bytes, bytes]:
    """
    Implements PBKDF2 with SHA256 similar to Django's password hasher
    """
    if salt is None:
        salt = os.urandom(8)  # Generate 8 random bytes for salt
    
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')

    # Use the built-in pbkdf2_hmac function
    key = hashlib.pbkdf2_hmac(
        'sha256',  # Hash algorithm
        password,  # Password to hash
        salt,      # Salt for the hash
        iterations,# Number of iterations
        32        # Length of the key
    )
    
    return key, salt

def format_hash(hashed: bytes, salt: bytes, iterations: int = 390000) -> str:
    """
    Formats the hash in Django's style: algorithm$iterations$salt$hash
    """
    salt_b64 = base64.b64encode(salt).decode('ascii').strip()
    hash_b64 = base64.b64encode(hashed).decode('ascii').strip()
    
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"

def test_password_hashing():
    # Get password from user
    password = input("Enter a password to hash: ")
    
    # Generate hash
    hashed, salt = derive_pbkdf2(password)
    formatted_hash = format_hash(hashed, salt)
    
    print("\nHashed password:", formatted_hash)
    print("\nHash format explanation:")
    print("- Format: pbkdf2_sha256$<iterations>$<salt>$<hash>")
    print("- Algorithm: PBKDF2 (Password-Based Key Derivation Function 2)")
    print("- Hash function: SHA256")
    print("- Iterations: 390000 (Django's default)")
    print("- Salt size: 8 bytes (encoded in base64)")
    
    # Verify
    verify_password = input("\nEnter the password again to verify: ")
    verify_hash, _ = derive_pbkdf2(verify_password, salt)  # Use same salt
    verify_formatted = format_hash(verify_hash, salt)
    
    is_valid = verify_formatted == formatted_hash
    print("\nPassword verification:", "Success" if is_valid else "Failed")
    
    # Show comparison
    if not is_valid:
        print("\nOriginal hash:", formatted_hash)
        print("Verify hash:  ", verify_formatted)

if __name__ == "__main__":
    test_password_hashing()