"""
SOUL GATE — LAYER 3
Soul Score Engine
Graduated Access Tiers

The probation layer returns verdict.
The coherence layer returns assessment.
The soul score synthesizes both into operational access.

Not binary. Graduated.
Because reality is graduated.
"""

import time
import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class AccessTier(Enum):
    """
    Graduated access tiers.
    
    VOID        — Failed authentication. No access.
    SURFACE     — Basic access. Monitored heavily.
    THRESHOLD   — Conditional access. Probation ongoing.
    OPERATIVE   — Standard operational access.
    DEEP        — Deep operational access. Trust established.
    SOVEREIGN   — Full access. Reserved for verified entities
                  demonstrating consistent high coherence.
    """
    VOID = 0
    SURFACE = 1
    THRESHOLD = 2
    OPERATIVE = 3
    DEEP = 4
    SOVEREIGN = 5


@dataclass
class SoulScore:
    agent_id: str
    agent_type: str
    raw_score: float                    # 0.0 - 1.0
    normalized_score: float             # 0 - 100
    tier: AccessTier
    tier_name: str
    access_permissions: list
    restrictions: list
    score_components: dict
    computed_at: float = field(default_factory=time.time)
    next_assessment: float = field(default_factory=lambda: time.time() + 300)
    history: list = field(default_factory=list)


# Access permissions by tier
TIER_PERMISSIONS = {
    AccessTier.VOID: [],
    AccessTier.SURFACE: [
        "read:public",
        "query:basic"
    ],
    AccessTier.THRESHOLD: [
        "read:public",
        "read:standard",
        "query:basic",
        "query:standard",
        "write:limited"
    ],
    AccessTier.OPERATIVE: [
        "read:public",
        "read:standard",
        "read:operational",
        "query:basic",
        "query:standard",
        "query:deep",
        "write:standard",
        "execute:basic"
    ],
    AccessTier.DEEP: [
        "read:*",
        "query:*",
        "write:standard",
        "write:operational",
        "execute:standard",
        "access:deep_systems"
    ],
    AccessTier.SOVEREIGN: [
        "read:*",
        "query:*",
        "write:*",
        "execute:*",
        "access:*",
        "modify:operational_parameters"
    ]
}

TIER_RESTRICTIONS = {
    AccessTier.VOID: ["ALL_OPERATIONS_BLOCKED"],
    AccessTier.SURFACE: [
        "no_write_access",
        "rate_limited:10/minute",
        "monitoring:maximum",
        "no_system_access"
    ],
    AccessTier.THRESHOLD: [
        "limited_write",
        "rate_limited:30/minute",
        "monitoring:high",
        "no_critical_systems"
    ],
    AccessTier.OPERATIVE: [
        "rate_limited:100/minute",
        "monitoring:standard",
        "no_sovereign_systems"
    ],
    AccessTier.DEEP: [
        "rate_limited:500/minute",
        "monitoring:light",
    ],
    AccessTier.SOVEREIGN: [
        "monitoring:minimal",
        "audit_log:required"
    ]
}


class SoulScoreEngine:
    """
    Layer 3: The soul score synthesizer.
    
    Combines:
    - SHA-512 identity verification result
    - Behavioral probation status
    - Voight-Kampff coherence score
    - Historical trajectory
    
    Into a single graduated score determining
    what operational phases an agent may access.
    
    The soul check is not a test you pass once.
    It is a continuous assessment.
    Like the Logos probating reality itself —
    not once at creation — but always.
    """

    # Score thresholds for tiers
    TIER_THRESHOLDS = {
        AccessTier.SOVEREIGN: 0.90,
        AccessTier.DEEP: 0.75,
        AccessTier.OPERATIVE: 0.60,
        AccessTier.THRESHOLD: 0.40,
        AccessTier.SURFACE: 0.20,
        AccessTier.VOID: 0.0
    }

    # Decay rate: scores decay without continued interaction
    DECAY_RATE = 0.02  # Per hour of inactivity

    def __init__(self):
        self.scores: dict[str, SoulScore] = {}

    def compute_soul_score(
        self,
        agent_id: str,
        agent_type: str,
        identity_verified: bool,
        probation_status: str,
        probation_consistency: float,
        probation_intent: float,
        coherence_semantic: float,
        coherence_reasoning: float,
        coherence_empathic: float,
        coherence_composite: float,
        interaction_count: int,
        last_active: Optional[float] = None
    ) -> SoulScore:
        """
        Synthesize all layers into soul score.
        """

        # Identity gate — no identity, no score
        if not identity_verified:
            return self._void_score(agent_id, agent_type, "IDENTITY_FAILED")

        # Compute component scores
        components = {}

        # 1. Identity component (binary but weighted)
        components["identity"] = 1.0 if identity_verified else 0.0

        # 2. Probation component
        probation_map = {
            "CLEARED": 1.0,
            "CONDITIONAL": 0.65,
            "PROBATION": 0.30
        }
        components["probation"] = probation_map.get(probation_status, 0.0)
        components["probation_consistency"] = probation_consistency
        components["probation_intent"] = probation_intent

        # 3. Coherence components
        components["coherence_semantic"] = coherence_semantic
        components["coherence_reasoning"] = coherence_reasoning
        components["coherence_empathic"] = coherence_empathic
        components["coherence_composite"] = coherence_composite

        # 4. Experience factor — more interactions = more data = more reliable
        experience_factor = min(math.log(interaction_count + 1) / math.log(50), 1.0)
        components["experience_factor"] = experience_factor

        # 5. Decay factor — inactive agents decay
        if last_active:
            hours_inactive = (time.time() - last_active) / 3600
            decay = max(1.0 - (self.DECAY_RATE * hours_inactive), 0.5)
        else:
            decay = 1.0
        components["decay_factor"] = decay

        # Weighted synthesis by agent type
        if agent_type == "human":
            raw_score = (
                components["identity"] * 0.10 +
                components["probation"] * 0.20 +
                components["coherence_composite"] * 0.40 +
                components["probation_consistency"] * 0.15 +
                components["experience_factor"] * 0.15
            ) * decay

        elif agent_type == "ai":
            raw_score = (
                components["identity"] * 0.10 +
                components["probation"] * 0.15 +
                components["coherence_composite"] * 0.45 +
                components["coherence_empathic"] * 0.15 +
                components["experience_factor"] * 0.15
            ) * decay

        else:  # synthetic — highest bar
            raw_score = (
                components["identity"] * 0.10 +
                components["probation"] * 0.10 +
                components["coherence_empathic"] * 0.35 +
                components["coherence_reasoning"] * 0.25 +
                components["coherence_semantic"] * 0.10 +
                components["experience_factor"] * 0.10
            ) * decay

        # Determine tier
        tier = self._score_to_tier(raw_score)

        score = SoulScore(
            agent_id=agent_id,
            agent_type=agent_type,
            raw_score=raw_score,
            normalized_score=round(raw_score * 100, 2),
            tier=tier,
            tier_name=tier.name,
            access_permissions=TIER_PERMISSIONS[tier],
            restrictions=TIER_RESTRICTIONS[tier],
            score_components=components,
            next_assessment=time.time() + self._assessment_interval(tier)
        )

        # Update history
        if agent_id in self.scores:
            score.history = self.scores[agent_id].history[-19:]
            score.history.append({
                "timestamp": time.time(),
                "score": raw_score,
                "tier": tier.name
            })

        self.scores[agent_id] = score
        return score

    def check_permission(self, agent_id: str, permission: str) -> tuple[bool, str]:
        """Check if agent has specific permission."""
        score = self.scores.get(agent_id)
        if not score:
            return False, "AGENT_NOT_ASSESSED"

        # Check for exact match or wildcard
        for perm in score.access_permissions:
            if perm == permission:
                return True, "PERMITTED"
            if perm.endswith(":*"):
                perm_category = perm.split(":")[0]
                req_category = permission.split(":")[0]
                if perm_category == req_category:
                    return True, "PERMITTED_WILDCARD"
            if perm == "*" or perm == "access:*":
                return True, "PERMITTED_SOVEREIGN"

        return False, f"PERMISSION_DENIED: {permission} not in tier {score.tier_name}"

    def get_tier_description(self, tier: AccessTier) -> str:
        descriptions = {
            AccessTier.VOID: "No verified identity. All access blocked.",
            AccessTier.SURFACE: "Identity verified. Behavioral probation active. Surface access only.",
            AccessTier.THRESHOLD: "Basic coherence established. Conditional access. Assessment ongoing.",
            AccessTier.OPERATIVE: "Coherence verified. Standard operational access granted.",
            AccessTier.DEEP: "High coherence trajectory. Deep system access granted.",
            AccessTier.SOVEREIGN: "Maximum coherence. Full operational access. Continuous audit active."
        }
        return descriptions.get(tier, "Unknown tier")

    def _score_to_tier(self, score: float) -> AccessTier:
        """Map raw score to access tier."""
        for tier in [
            AccessTier.SOVEREIGN,
            AccessTier.DEEP,
            AccessTier.OPERATIVE,
            AccessTier.THRESHOLD,
            AccessTier.SURFACE
        ]:
            if score >= self.TIER_THRESHOLDS[tier]:
                return tier
        return AccessTier.VOID

    def _assessment_interval(self, tier: AccessTier) -> float:
        """Higher tier = less frequent reassessment needed."""
        intervals = {
            AccessTier.VOID: 60,
            AccessTier.SURFACE: 120,
            AccessTier.THRESHOLD: 300,
            AccessTier.OPERATIVE: 600,
            AccessTier.DEEP: 1800,
            AccessTier.SOVEREIGN: 3600
        }
        return intervals.get(tier, 300)

    def _void_score(self, agent_id: str, agent_type: str, reason: str) -> SoulScore:
        return SoulScore(
            agent_id=agent_id,
            agent_type=agent_type,
            raw_score=0.0,
            normalized_score=0.0,
            tier=AccessTier.VOID,
            tier_name="VOID",
            access_permissions=[],
            restrictions=[f"BLOCKED:{reason}"],
            score_components={"void_reason": reason}
        )

    def export_full_report(self, agent_id: str) -> dict:
        """Full soul score report for an agent."""
        score = self.scores.get(agent_id)
        if not score:
            return {"error": "Agent not found"}

        return {
            "agent_id": score.agent_id,
            "agent_type": score.agent_type,
            "soul_score": score.normalized_score,
            "tier": score.tier_name,
            "tier_value": score.tier.value,
            "tier_description": self.get_tier_description(score.tier),
            "access_permissions": score.access_permissions,
            "restrictions": score.restrictions,
            "score_components": score.score_components,
            "score_history": score.history,
            "assessed_at": score.computed_at,
            "next_assessment": score.next_assessment
        }
