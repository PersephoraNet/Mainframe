import hashlib


SECRET_KEY = "01010111010110001010111010100010100110101110010111"

# SHA-512 hash of the secret key
KEY_HASH = "61027e050186ecfca69db93c7301fed2a37995e1e9d2ace74c54a4d4b8b8806b818662c0c3490ca17879a0e5dfbe18d1ceb285bbaca83176216c10fcd3981e44"


def get_key_hash() -> str:
    """Returns the SHA-512 hash of the secret key."""
    return KEY_HASH


def verify_key(input_key: str) -> bool:
    """Verify an input key against the stored SHA-512 hash."""
    input_hash = hashlib.sha512(input_key.encode("utf-8")).hexdigest()
    return input_hash == KEY_HASH


if __name__ == "__main__":
    print(f"SHA-512 Hash: {KEY_HASH}")
    print(f"Verified: {verify_key(SECRET_KEY)}")
