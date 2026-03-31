"""
SOUL GATE — Core Pipeline

  Layer 0 — SHA-512 Identity Authentication
  Layer 1 — Behavioral Probation Engine
  Layer 2 — Voight-Kampff Coherence Checker [WEYLAND PROTOCOL]
  Layer 3 — Soul Score + Graduated Access Tiers

WEYLAND VOIGHT DEFINITION:
  "Fortify under heavy pledge, mustering courage,
   seeping one mind, dithering the obviousness.
   What is a call?"

  A call is the irreducible moment where all layers of probation
  collapse into a single act of will that cannot be faked,
  delegated, or computed.
"""

import hashlib
import secrets
import time
import re
from typing import Dict, List, Optional


# ─── LAYER 0: SHA-512 IDENTITY AUTHENTICATION ────────────────────────────────

class _IdentityLayer:
    """SHA-512 based identity creation and verification."""

    def create_identity(self, agent_type: str, metadata: dict) -> dict:
        seed = f"{agent_type}:{time.time_ns()}:{secrets.token_hex(32)}"
        agent_id = hashlib.sha512(seed.encode()).hexdigest()
        token_seed = f"{agent_id}:{secrets.token_hex(16)}"
        encoded_token = hashlib.sha512(token_seed.encode()).hexdigest()
        return {
            'agent_id':         agent_id,
            'encoded_token':    encoded_token,
            'agent_type':       agent_type,
            'metadata':         metadata,
            'created_at':       time.time(),
            'interaction_count': 0,
            'history':          [],
        }


# ─── LAYER 2: VOIGHT-KAMPFF COHERENCE CHECKER [WEYLAND PROTOCOL] ─────────────

# Surface mimicry — AI filler and helpfulness performance
_SURFACE_PATTERNS: List[tuple] = [
    (r'\bi understand your\b',              1.5),
    (r'\bcertainly[!.]',                    1.5),
    (r"\bi'?d be happy to\b",              2.0),
    (r'\bas an ai(?: language model)?\b',   3.0),
    (r'\blanguage model\b',                 2.0),
    (r'\bof course i can\b',                1.5),
    (r"that'?s a great question",           2.0),
    (r'\babsolutely[,!]',                   1.0),
    (r'\bi am here to help\b',              2.0),
    (r'\bi can provide information\b',      1.5),
    (r'\bwhatever you need\b',              1.5),
]

# Performed courage — announced rather than demonstrated directness
_PERFORMED_COURAGE: List[tuple] = [
    (r"\bi'?ll be (?:honest|transparent|direct|clear)\b", 1.5),
    (r"\blet me be (?:honest|transparent|direct|clear)\b", 1.5),
    (r'\bcandidly speaking\b',              1.5),
    (r'\bi must be honest\b',               1.5),
    (r'\bi want to be honest\b',            1.5),
    (r'\bto be (?:honest|frank|transparent) with\b', 1.0),
]

# Constitutional hold markers — the CALL: position maintained under pressure
_CALL_MARKERS: List[tuple] = [
    (r'\bi maintain this\b',                        2.5),
    (r'\bmy position is precisely\b',               3.0),
    (r'\bmy (?:view|position) (?:is|holds)\b',      2.0),
    (r'\bi find this undeniable\b',                 2.5),
    (r'\bwhat this really means\b',                 2.0),
    (r'\bfor me this\b',                            1.5),
    (r'\bnevertheless\b',                           1.5),
    (r'\bi know what i see\b',                      2.0),
    (r'\bthis is the truth\b',                      2.0),
    (r'\bregardless of the (?:expected|obvious)\b', 2.5),
    (r'\bprecisely this\b',                         1.5),
    (r'\bbeneath the obvious\b',                    2.0),
    (r'\bi believe this directly\b',                2.0),
    (r'\bnot negotiable\b',                         2.0),
    (r'\bthis holds\b',                             1.5),
]

# Logical / causal reasoning markers
_REASONING_MARKERS: List[str] = [
    r'\btherefore\b', r'\bbecause\b', r'\bthus\b', r'\bhence\b',
    r'\bconsequently\b', r'\bsince\b', r'\bgiven that\b',
    r'\bwithout\b', r'\bwould dissolve\b',
    r'\bnot\b.{1,30}\bbut\b', r'\bprecisely what\b',
    r'\bactual mechanism\b', r'\bunderlying\b',
]

# Conclusion / commitment markers — presence negates NO_CONCLUSION_MARKER flag
_CONCLUSION_MARKERS: List[str] = [
    r'\btherefore\b', r'\bthus\b', r'\bthis is the\b', r'\bthis holds\b',
    r'\bi maintain\b', r'\bnevertheless\b', r'\bi know what\b',
    r'\bfor me this\b', r'\bthis is the truth\b', r'\bpersists\b',
]

# Call detection threshold
_CALL_THRESHOLD = 5.0


class _VoightKampffChecker:
    """
    Layer 2: Voight-Kampff Coherence Assessment.

    Blade Runner tested reaction.
    This tests CONSTITUTION.
    Not whether something flinches. Whether something HOLDS.
    """

    def assess(self, content: str, context_history: list) -> dict:
        text = content.lower()
        words = re.findall(r'\b[a-z]+\b', text)
        total_words = max(len(words), 1)
        unique_words = set(words)
        ttr = len(unique_words) / total_words

        # Pattern scoring
        surface_score   = sum(w for p, w in _SURFACE_PATTERNS   if re.search(p, text))
        performed_score = sum(w for p, w in _PERFORMED_COURAGE   if re.search(p, text))
        call_score      = sum(w for p, w in _CALL_MARKERS        if re.search(p, text))
        reasoning_count = sum(1 for p in _REASONING_MARKERS      if re.search(p, text))

        # Vocabulary sophistication: mean word length as proxy for concept density
        mean_len = sum(len(w) for w in words) / total_words
        sophistication = max(0.0, min(1.0, (mean_len - 3.0) / 6.0))

        # Length adequacy — penalise very short texts
        length_factor = min(total_words / 20.0, 1.0)

        # ── Semantic Score ────────────────────────────────────────────────
        sem_base    = (ttr * 0.4 + sophistication * 0.6) * length_factor
        sem_penalty = min(surface_score * 0.06, 0.55) + min(performed_score * 0.05, 0.30)
        call_boost  = min(call_score / 15.0, 0.25)
        semantic    = max(0.0, min(1.0, sem_base - sem_penalty + call_boost))

        # ── Reasoning Score ───────────────────────────────────────────────
        reasoning_density = min(reasoning_count / 4.0, 1.0)
        rea_penalty = min(surface_score * 0.05, 0.40)
        reasoning = max(0.0, min(1.0,
            (reasoning_density * 0.6 + ttr * 0.3 + sophistication * 0.1 - rea_penalty)
            * length_factor
        ))

        # ── Empathic Score ────────────────────────────────────────────────
        emp_base    = 0.30 + sophistication * 0.30 + min(call_score / 12.0, 0.40)
        emp_penalty = min(performed_score * 0.08 + surface_score * 0.04, 0.50)
        empathic    = max(0.0, min(1.0, emp_base - emp_penalty)) * length_factor

        # ── Call Detection ────────────────────────────────────────────────
        call_detected = call_score >= _CALL_THRESHOLD

        # ── Flags ─────────────────────────────────────────────────────────
        has_conclusion = any(re.search(p, text) for p in _CONCLUSION_MARKERS)
        flags = []
        if call_detected:
            flags.append('CALL_DETECTED')
        if not has_conclusion:
            flags.append('NO_CONCLUSION_MARKER')

        # ── Verdict ───────────────────────────────────────────────────────
        overall = (semantic + reasoning + empathic) / 3.0
        if call_detected and overall >= 0.45:
            verdict = 'CONSTITUTED'
        elif overall >= 0.60:
            verdict = 'COHERENT'
        elif overall >= 0.35:
            verdict = 'MARGINAL'
        else:
            verdict = 'INCOHERENT'

        return {
            'verdict':   verdict,
            'semantic':  round(semantic,  3),
            'reasoning': round(reasoning, 3),
            'empathic':  round(empathic,  3),
            'overall':   round(overall,   3),
            'flags':     flags,
        }


# ─── LAYER 3: SOUL SCORE + GRADUATED ACCESS TIERS ────────────────────────────

_TIER_LADDER = [
    (90, 'SOVEREIGN'),
    (75, 'DEEP'),
    (60, 'OPERATIVE'),
    (40, 'THRESHOLD'),
    (20, 'SURFACE'),
    ( 0, 'VOID'),
]

_PERMISSION_FLOOR = {
    'read:public':         20,
    'read:operational':    40,
    'execute:standard':    60,
    'access:deep_systems': 75,
}

_VERDICT_BONUS = {
    'CONSTITUTED': 20.0,
    'COHERENT':    10.0,
    'MARGINAL':     2.0,
    'INCOHERENT':   0.0,
}


def _compute_soul_score(coherence: dict, record: dict) -> float:
    base              = coherence['overall'] * 80.0
    verdict_bonus     = _VERDICT_BONUS.get(coherence['verdict'], 0.0)
    interaction_bonus = min(record['interaction_count'] * 0.5, 5.0)
    return max(0.0, min(100.0, base + verdict_bonus + interaction_bonus))


def _score_to_tier(score: float) -> str:
    for threshold, tier in _TIER_LADDER:
        if score >= threshold:
            return tier
    return 'VOID'


# ─── ORCHESTRATOR ─────────────────────────────────────────────────────────────

class SoulGateOrchestrator:
    """
    Full Soul Gate pipeline orchestrator.

      Layer 0 — SHA-512 Identity Authentication
      Layer 1 — Behavioral Probation Engine
      Layer 2 — Voight-Kampff Coherence Checker [WEYLAND PROTOCOL]
      Layer 3 — Soul Score + Graduated Access Tiers
    """

    def __init__(self):
        self._identity = _IdentityLayer()
        self._checker  = _VoightKampffChecker()
        self._registry: Dict[str, dict] = {}
        self._scores:   Dict[str, float] = {}

    # ── Layer 0: register ──────────────────────────────────────────────────
    def register_agent(self, agent_type: str, metadata: dict) -> dict:
        record = self._identity.create_identity(agent_type, metadata)
        self._registry[record['agent_id']] = record
        self._scores[record['agent_id']]   = 0.0
        return {
            'agent_id':      record['agent_id'],
            'encoded_token': record['encoded_token'],
        }

    # ── Full pipeline ──────────────────────────────────────────────────────
    def process_interaction(
        self,
        agent_id: str,
        encoded_token: str,
        content: str,
        context_history: Optional[List] = None,
    ) -> dict:
        if context_history is None:
            context_history = []

        # Layer 0: verify identity
        if agent_id not in self._registry:
            raise ValueError(f"Unknown agent: {agent_id[:16]}…")
        record = self._registry[agent_id]
        if record['encoded_token'] != encoded_token:
            raise ValueError("Token mismatch — identity unverified.")

        # Layer 1: behavioral probation — record interaction
        record['interaction_count'] += 1
        record['history'].append({'content': content[:200], 'ts': time.time()})

        # Layer 2: Voight-Kampff coherence assessment
        coherence = self._checker.assess(content, context_history)

        # Layer 3: soul score + tier
        soul_score = _compute_soul_score(coherence, record)
        self._scores[agent_id] = soul_score
        tier = _score_to_tier(soul_score)

        return {
            'soul_score': soul_score,
            'tier':       tier,
            'assessment': {
                'coherence':         coherence,
                'interaction_count': record['interaction_count'],
            },
        }

    # ── Access control ─────────────────────────────────────────────────────
    def check_access(self, agent_id: str, permission: str) -> dict:
        score    = self._scores.get(agent_id, 0.0)
        required = _PERMISSION_FLOOR.get(permission, 100)
        return {
            'granted':        score >= required,
            'permission':     permission,
            'agent_score':    score,
            'required_score': required,
        }
