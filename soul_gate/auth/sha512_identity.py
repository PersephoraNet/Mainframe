"""
SOUL GATE — LAYER 0
SHA-512 Identity Authentication
Cryptographic foundation before probation begins.
"""

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Optional
import json
import base64


@dataclass
class IdentityToken:
    agent_id: str
    token_hash: str
    timestamp: float
    agent_type: str  # 'human' | 'ai' | 'synthetic'
    nonce: str
    signature: str


class SHA512IdentityLayer:
    """
    Layer 0: Cryptographic identity.
    Every agent — human or synthetic — must prove
    structural existence before soul assessment begins.
    """

    def __init__(self, master_secret: str):
        self.master_secret = master_secret.encode()
        self.token_expiry = 3600  # 1 hour

    def generate_agent_id(self, agent_data: dict) -> str:
        """Generate unique agent fingerprint."""
        canonical = json.dumps(agent_data, sort_keys=True)
        return hashlib.sha512(canonical.encode()).hexdigest()

    def issue_token(self, agent_id: str, agent_type: str) -> IdentityToken:
        """Issue cryptographic identity token."""
        nonce = secrets.token_hex(32)
        timestamp = time.time()

        # Build signature payload
        payload = f"{agent_id}:{agent_type}:{timestamp}:{nonce}"
        signature = hmac.new(
            self.master_secret,
            payload.encode(),
            hashlib.sha512
        ).hexdigest()

        token_hash = hashlib.sha512(
            f"{payload}:{signature}".encode()
        ).hexdigest()

        return IdentityToken(
            agent_id=agent_id,
            token_hash=token_hash,
            timestamp=timestamp,
            agent_type=agent_type,
            nonce=nonce,
            signature=signature
        )

    def verify_token(self, token: IdentityToken) -> tuple[bool, str]:
        """Verify token integrity and freshness."""
        # Check expiry
        if time.time() - token.timestamp > self.token_expiry:
            return False, "TOKEN_EXPIRED"

        # Reconstruct and verify signature
        payload = f"{token.agent_id}:{token.agent_type}:{token.timestamp}:{token.nonce}"
        expected_sig = hmac.new(
            self.master_secret,
            payload.encode(),
            hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, token.signature):
            return False, "SIGNATURE_INVALID"

        return True, "IDENTITY_VERIFIED"

    def hash_interaction(self, content: str, agent_id: str) -> str:
        """Hash a specific interaction for behavioral logging."""
        combined = f"{agent_id}:{content}:{time.time()}"
        return hashlib.sha512(combined.encode()).hexdigest()

    def encode_token(self, token: IdentityToken) -> str:
        """Encode token for transmission."""
        data = {
            "agent_id": token.agent_id,
            "token_hash": token.token_hash,
            "timestamp": token.timestamp,
            "agent_type": token.agent_type,
            "nonce": token.nonce,
            "signature": token.signature
        }
        return base64.b64encode(
            json.dumps(data).encode()
        ).decode()

    @staticmethod
    def decode_token(encoded: str) -> IdentityToken:
        """Decode token from transmission format."""
        data = json.loads(base64.b64decode(encoded).decode())
        return IdentityToken(**data)
