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
    4. If granted: compute session words from live key
    5. Record word chain as behavioral ledger entry (wallet model)
    6. Return KEY_HASH for the flip

The word chain is the session's cryptographic identity — deterministic,
reproducible, unique to session_id + key. Like a BIP-39 seed phrase,
the words carry no semantic meaning but carry full identity meaning.
Each flip appends a verifiable entry to the agent's behavioral history.
Same session_id always produces same word chain — maximum consistency.
"""

import hashlib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

WORDLIST = [
    "daemon", "libra", "epsylon", "zeta", "obvious", "target",
    "game", "live", "powder", "corn", "visual", "instance",
    "refraction", "life", "long", "dispatch", "essence"
]


def _derive_words(session_id: str, key_hash: str, count: int = 7) -> list:
    seed = hashlib.sha512(f"{session_id}:{key_hash}".encode()).hexdigest()
    selected, seen, i = [], set(), 0
    while len(selected) < count and i < len(seed) - 1:
        index = int(seed[i:i + 2], 16) % len(WORDLIST)
        word = WORDLIST[index]
        if word not in seen:
            seen.add(word)
            selected.append(word)
        i += 2
    for word in WORDLIST:
        if len(selected) >= count:
            break
        if word not in seen:
            selected.append(word)
            seen.add(word)
    return selected


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

        After key retrieval, the session word chain is computed and recorded
        as a behavioral ledger entry — the flip's cryptographic identity
        appended to the agent's Soul Gate history.
        """
        agent = self.gate.register_agent(agent_type, agent_metadata or {})

        # Pass 1: session_id as content — establishes identity, runs full pipeline
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

        # Compute session words — the flip's cryptographic identity
        words = _derive_words(session_id, key_hash)
        word_chain = "-".join(words)

        # Pass 2: record word chain as behavioral ledger entry
        # The word chain is deterministic and reproducible — same session_id
        # always produces the same chain, registering as consistent behavior.
        content_hash = self.gate.identity.hash_interaction(word_chain, agent["agent_id"])
        self.gate.probation.record_interaction(
            agent_id=agent["agent_id"],
            content=word_chain,
            content_hash=content_hash,
            agent_type=agent_type,
        )

        return {
            "granted": True,
            "session_id": session_id,
            "agent_id": agent["agent_id"],
            "tier": vault_result["tier"],
            "soul_score": vault_result["soul_score"],
            "key_hash": key_hash,
            "word_chain": word_chain,
        }
