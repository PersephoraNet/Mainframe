"""
SOUL GATE — KEY VAULT

Gates access to secret.key through the full four-layer Soul Gate pipeline.
No agent reads or rotates the key by declaration — only by demonstrated coherence.

Access tiers required:

    READ   → DEEP tier     (access:deep_systems)
    ROTATE → OBERON tier (modify:operational_parameters)

The Soul Gate pipeline runs in full for every vault request:
    Layer 0 — SHA-512 identity verification
    Layer 1 — Behavioral probation assessment
    Layer 2 — Voight-Kampff coherence check
    Layer 3 — Soul score computation and tier assignment
"""

import os
import hashlib
import time

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "secret.key")

READ_PERMISSION   = "access:deep_systems"       # DEEP tier
ROTATE_PERMISSION = "modify:operational_parameters"  # OBERON tier


class KeyVault:
    """
    Wraps secret.key behind the Soul Gate pipeline.

    Every read or rotate request runs the agent through all four layers.
    Tier is computed fresh on each request — no cached grants.
    """

    def __init__(self, gate, key_path: str = None):
        self.gate = gate
        self.key_path = os.path.abspath(key_path or KEY_FILE)

    def read(self, agent_id: str, encoded_token: str, content: str) -> dict:
        """
        Read secret.key.
        Requires DEEP tier (access:deep_systems).
        Runs full Soul Gate pipeline on every call.
        """
        assessment = self.gate.process_interaction(agent_id, encoded_token, content)

        if not assessment.get("success"):
            return self._denied(
                agent_id,
                assessment.get("message", "PIPELINE_FAILED"),
                assessment
            )

        access = self.gate.check_access(agent_id, READ_PERMISSION)
        if not access["granted"]:
            return self._denied(
                agent_id,
                f"TIER_INSUFFICIENT: {assessment['tier']} — DEEP required for key read",
                assessment
            )

        return {
            "granted": True,
            "operation": "READ",
            "agent_id": agent_id,
            "key": self._load_key(),
            "tier": assessment["tier"],
            "soul_score": assessment["soul_score"],
            "timestamp": time.time(),
        }

    def rotate(self, agent_id: str, encoded_token: str, content: str) -> dict:
        """
        Rotate secret.key.
        Requires OBERON tier (modify:operational_parameters).
        Generates new key from os.urandom(32), writes to disk.
        Returns SHA-512 hash of new key — not the key itself.
        """
        assessment = self.gate.process_interaction(agent_id, encoded_token, content)

        if not assessment.get("success"):
            return self._denied(
                agent_id,
                assessment.get("message", "PIPELINE_FAILED"),
                assessment
            )

        access = self.gate.check_access(agent_id, ROTATE_PERMISSION)
        if not access["granted"]:
            return self._denied(
                agent_id,
                f"TIER_INSUFFICIENT: {assessment['tier']} — OBERON required for key rotation",
                assessment
            )

        new_key = self._rotate_key()
        new_hash = hashlib.sha512(new_key.encode()).hexdigest()

        return {
            "granted": True,
            "operation": "ROTATE",
            "agent_id": agent_id,
            "new_key_hash": new_hash,
            "tier": assessment["tier"],
            "soul_score": assessment["soul_score"],
            "rotated_at": time.time(),
        }

    def _load_key(self) -> str:
        with open(self.key_path) as f:
            return f.read().strip()

    def _rotate_key(self) -> str:
        raw = os.urandom(32)
        binary = "".join(f"{byte:08b}" for byte in raw)
        with open(self.key_path, "w") as f:
            f.write(binary + "\n")
        return binary

    def _denied(self, agent_id: str, reason: str, assessment: dict) -> dict:
        return {
            "granted": False,
            "operation": None,
            "agent_id": agent_id,
            "reason": reason,
            "tier": assessment.get("tier", "VOID"),
            "soul_score": assessment.get("soul_score", 0.0),
            "timestamp": time.time(),
        }
