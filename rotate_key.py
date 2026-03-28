"""
rotate_key.py — Secret key rotation utility

Generates a new cryptographic key, hashes it with SHA-512,
and updates secret.key and key_hash.py in place.

Usage:
    python rotate_key.py
"""
import os
import hashlib
import base64
from datetime import datetime, timezone

KEY_FILE = "secret.key"
HASH_FILE = "key_hash.py"


def generate_key() -> tuple:
    raw = os.urandom(32)
    b64 = base64.b64encode(raw).decode("utf-8")
    binary = "".join(f"{byte:08b}" for byte in raw)
    return raw, b64, binary


def hash_key(key_str: str) -> str:
    return hashlib.sha512(key_str.encode("utf-8")).hexdigest()


def update_key_file(binary_key: str):
    with open(KEY_FILE, "w") as f:
        f.write(binary_key + "\n")


def update_hash_file(new_hash: str, rotated_at: str):
    content = f'''import hashlib


SECRET_KEY_HASH = "{new_hash}"
ROTATED_AT = "{rotated_at}"


def get_key_hash() -> str:
    """Returns the SHA-512 hash of the current secret key."""
    return SECRET_KEY_HASH


def verify_key(input_key: str) -> bool:
    """Verify an input key against the stored SHA-512 hash."""
    input_hash = hashlib.sha512(input_key.encode("utf-8")).hexdigest()
    return input_hash == SECRET_KEY_HASH
'''
    with open(HASH_FILE, "w") as f:
        f.write(content)


def main():
    rotated_at = datetime.now(timezone.utc).isoformat()

    raw, b64, binary = generate_key()
    new_hash = hash_key(binary)

    print("=" * 60)
    print("  KEY ROTATION")
    print("=" * 60)
    print(f"  Rotated at   : {rotated_at}")
    print(f"  New key (b64): {b64}")
    print(f"  New SHA-512  : {new_hash[:32]}...")
    print("=" * 60)

    update_key_file(binary)
    update_hash_file(new_hash, rotated_at)

    print(f"\n  Updated: {KEY_FILE}")
    print(f"  Updated: {HASH_FILE}")
    print("\n  IMPORTANT: commit both files and redeploy any services")
    print("  using this key. Do NOT commit secret.key to git.")


if __name__ == "__main__":
    main()
