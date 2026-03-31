"""
SOUL GATE — FLIP GATE

Gates coin flip access behind the full Soul Gate pipeline.
The flip's KEY_HASH is derived from secret.key, which is held by the vault.

An agent that cannot reach DEEP tier cannot retrieve the key,
and therefore cannot run a verifiable flip.

Flow:
    1. Register agent with Soul Gate
    2. Submit session_id as interaction content for assessment
    3. Vault checks DEEP tier (access:deep_systems)
    4. If granted: return sha512(key) for use as KEY_HASH in flip
    5. If denied:  return reason and current tier
"""

import hashlib


class FlipGate:
    """
    Bridges the coin flip and the Key Vault.

    Usage:
        gate = SoulGateOrchestrator()
        fg = FlipGate(gate)
        result = fg.request(agent_type="human", session_id="run-123")
        if result["granted"]:
            key_hash = result["key_hash"]
            # pass to flip_coin(session_id, key_hash=key_hash)
    """

    def __init__(self, gate):
        from vault.key_vault import KeyVault
        self.gate = gate
        self.vault = KeyVault(gate)

    def request(self, agent_type: str, session_id: str, agent_metadata: dict = None) -> dict:
        """
        Register agent, run Soul Gate assessment using session_id as content,
        and retrieve KEY_HASH if DEEP tier is reached.
        """
        agent = self.gate.register_agent(agent_type, agent_metadata or {})

        vault_result = self.vault.read(
            agent_id=agent["agent_id"],
            encoded_token=agent["encoded_token"],
            content=session_id,
        )

        if not vault_result["granted"]:
            return {
                "granted": False,
                "session_id": session_id,
                "agent_id": agent["agent_id"],
                "tier": vault_result["tier"],
                "soul_score": vault_result["soul_score"],
                "reason": vault_result["reason"],
            }

        raw_key = vault_result["key"]
        key_hash = hashlib.sha512(raw_key.encode("utf-8")).hexdigest()

        return {
            "granted": True,
            "session_id": session_id,
            "agent_id": agent["agent_id"],
            "tier": vault_result["tier"],
            "soul_score": vault_result["soul_score"],
            "key_hash": key_hash,
        }
