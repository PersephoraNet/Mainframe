"""
SOUL GATE — API LAYER
FastAPI Cloud Application

Orchestrates all four layers:
Layer 0: SHA-512 Identity
Layer 1: Behavioral Probation
Layer 2: Voight-Kampff Coherence
Layer 3: Soul Score

Cloud-ready. Stateless where possible.
Designed for horizontal scaling.
"""

import os
import sys
import time
import hashlib
import json
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, HTTPException, Header, Depends, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI not installed. Running in demo mode.")

from auth.sha512_identity import SHA512IdentityLayer, IdentityToken
from probation.behavioral_engine import BehavioralProbationEngine
from voight_kampff.coherence_checker import VoightKampffChecker
from scoring.soul_score import SoulScoreEngine, AccessTier
from vault.key_vault import KeyVault


# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

MASTER_SECRET = os.environ.get("SOUL_GATE_SECRET", "development_secret_change_in_production")
API_VERSION = "1.0.0"
SYSTEM_NAME = "SOUL GATE"

# ─────────────────────────────────────────
# INITIALIZE LAYERS
# ─────────────────────────────────────────

identity_layer = SHA512IdentityLayer(master_secret=MASTER_SECRET)
probation_engine = BehavioralProbationEngine()
coherence_checker = VoightKampffChecker()
soul_score_engine = SoulScoreEngine()

# ─────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────

if FASTAPI_AVAILABLE:
    class AgentRegistration(BaseModel):
        agent_type: str
        agent_metadata: dict = {}

    class InteractionSubmission(BaseModel):
        agent_id: str
        encoded_token: str
        content: str
        context_history: list = []

    class PermissionCheck(BaseModel):
        agent_id: str
        permission: str

    class SoulGateResponse(BaseModel):
        success: bool
        agent_id: str
        soul_score: float
        tier: str
        permissions: list
        message: str
        timestamp: float

    class VaultRequest(BaseModel):
        agent_id: str
        encoded_token: str
        content: str

# ─────────────────────────────────────────
# SOUL GATE ORCHESTRATOR
# ─────────────────────────────────────────

class SoulGateOrchestrator:
    """
    The complete Soul Gate pipeline.
    Can run with or without FastAPI.
    """

    def __init__(self):
        self.identity = identity_layer
        self.probation = probation_engine
        self.coherence = coherence_checker
        self.scoring = soul_score_engine

    def register_agent(self, agent_type: str, agent_metadata: dict = {}) -> dict:
        """Register new agent and issue identity token."""
        agent_data = {
            "type": agent_type,
            "metadata": agent_metadata,
            "registered_at": time.time()
        }

        agent_id = self.identity.generate_agent_id(agent_data)
        token = self.identity.issue_token(agent_id, agent_type)
        encoded_token = self.identity.encode_token(token)

        # Initialize probation record
        self.probation.register_agent(agent_id, agent_type)

        return {
            "agent_id": agent_id,
            "encoded_token": encoded_token,
            "token_expires_in": 3600,
            "message": "Identity established. Probation begins. Soul assessment pending.",
            "system": SYSTEM_NAME,
            "version": API_VERSION
        }

    def process_interaction(
        self,
        agent_id: str,
        encoded_token: str,
        content: str,
        context_history: list = []
    ) -> dict:
        """
        Full Soul Gate pipeline for a single interaction.
        """

        # ── LAYER 0: Identity Verification ──
        try:
            token = self.identity.decode_token(encoded_token)
        except Exception as e:
            return self._gate_response(
                False, agent_id, 0.0, "VOID",
                f"TOKEN_DECODE_FAILED: {str(e)}"
            )

        identity_valid, identity_msg = self.identity.verify_token(token)
        if not identity_valid:
            return self._gate_response(
                False, agent_id, 0.0, "VOID",
                f"IDENTITY_REJECTED: {identity_msg}"
            )

        # ── LAYER 1: Behavioral Probation ──
        content_hash = self.identity.hash_interaction(content, agent_id)
        probation_result = self.probation.record_interaction(
            agent_id=agent_id,
            content=content,
            content_hash=content_hash,
            agent_type=token.agent_type
        )

        # ── LAYER 2: Voight-Kampff Coherence ──
        coherence_result = self.coherence.assess(
            agent_id=agent_id,
            agent_type=token.agent_type,
            content=content,
            context_history=context_history
        )

        # ── LAYER 3: Soul Score ──
        probation_record = self.probation.get_record(agent_id)

        soul_score = self.scoring.compute_soul_score(
            agent_id=agent_id,
            agent_type=token.agent_type,
            identity_verified=True,
            probation_status=probation_result["status"],
            probation_consistency=probation_record.consistency_score if probation_record else 0.0,
            probation_intent=probation_record.intent_score if probation_record else 0.0,
            coherence_semantic=coherence_result.semantic_score,
            coherence_reasoning=coherence_result.reasoning_score,
            coherence_empathic=coherence_result.empathic_score,
            coherence_composite=coherence_result.composite_score,
            interaction_count=probation_result["interaction_count"],
            last_active=time.time()
        )

        # Build response
        return {
            "success": True,
            "agent_id": agent_id,
            "agent_type": token.agent_type,
            "soul_score": soul_score.normalized_score,
            "tier": soul_score.tier_name,
            "tier_value": soul_score.tier.value,
            "permissions": soul_score.access_permissions,
            "restrictions": soul_score.restrictions,
            "assessment": {
                "identity": {
                    "verified": True,
                    "message": identity_msg
                },
                "probation": {
                    "status": probation_result["status"],
                    "consistency": probation_record.consistency_score if probation_record else 0.0,
                    "intent": probation_record.intent_score if probation_record else 0.0,
                    "interactions_recorded": probation_result["interaction_count"]
                },
                "coherence": {
                    "verdict": coherence_result.verdict,
                    "semantic": coherence_result.semantic_score,
                    "reasoning": coherence_result.reasoning_score,
                    "empathic": coherence_result.empathic_score,
                    "composite": coherence_result.composite_score,
                    "flags": coherence_result.flags
                },
                "soul_components": soul_score.score_components
            },
            "message": self._tier_message(soul_score.tier),
            "timestamp": time.time(),
            "next_assessment": soul_score.next_assessment
        }

    def check_access(self, agent_id: str, permission: str) -> dict:
        """Check if agent has specific permission."""
        permitted, reason = self.scoring.check_permission(agent_id, permission)
        return {
            "agent_id": agent_id,
            "permission": permission,
            "granted": permitted,
            "reason": reason,
            "timestamp": time.time()
        }

    def get_full_report(self, agent_id: str) -> dict:
        """Get complete soul gate report for an agent."""
        soul_report = self.scoring.export_full_report(agent_id)
        behavioral_report = self.probation.export_trajectory(agent_id)
        coherence_cache = self.coherence.get_cached_result(agent_id)

        return {
            "agent_id": agent_id,
            "soul_report": soul_report,
            "behavioral_trajectory": behavioral_report,
            "last_coherence": {
                "verdict": coherence_cache.verdict,
                "composite": coherence_cache.composite_score,
                "timestamp": coherence_cache.timestamp
            } if coherence_cache else None,
            "generated_at": time.time()
        }

    def _tier_message(self, tier: AccessTier) -> str:
        messages = {
            AccessTier.VOID: "Access denied. Identity or coherence insufficient.",
            AccessTier.SURFACE: "Surface access granted. Probation active. Demonstrate consistent coherence.",
            AccessTier.THRESHOLD: "Threshold access granted. Conditional clearance. Assessment continues.",
            AccessTier.OPERATIVE: "Operative access granted. Coherence verified. Standard operations permitted.",
            AccessTier.DEEP: "Deep access granted. High coherence trajectory confirmed.",
            AccessTier.OBERON: "Oberon access granted. Maximum coherence. Full operational clearance.",
            AccessTier.SOVEREIGN: "Sovereign. 100%. Unrestricted."
        }
        return messages.get(tier, "Assessment complete.")

    def _gate_response(
        self, success: bool, agent_id: str,
        score: float, tier: str, message: str
    ) -> dict:
        return {
            "success": success,
            "agent_id": agent_id,
            "soul_score": score,
            "tier": tier,
            "permissions": [],
            "restrictions": ["ALL_BLOCKED"],
            "message": message,
            "timestamp": time.time()
        }


# ─────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────

gate = SoulGateOrchestrator()
vault = KeyVault(gate)

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="SOUL GATE",
        description="""
        Multi-layer access control system combining:
        - SHA-512 cryptographic identity
        - Behavioral probation engine  
        - Voight-Kampff coherence assessment
        - Graduated soul scoring
        
        For human and synthetic agents alike.
        """,
        version=API_VERSION
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.get("/")
    async def root():
        return {
            "system": SYSTEM_NAME,
            "version": API_VERSION,
            "status": "OPERATIONAL",
            "layers": [
                "Layer 0: SHA-512 Identity",
                "Layer 1: Behavioral Probation",
                "Layer 2: Voight-Kampff Coherence",
                "Layer 3: Soul Score"
            ],
            "message": "The gate is open. Passage requires coherence."
        }

    @app.post("/register")
    async def register_agent(registration: AgentRegistration):
        """Register a new agent and receive identity token."""
        return gate.register_agent(
            agent_type=registration.agent_type,
            agent_metadata=registration.agent_metadata
        )

    @app.post("/interact")
    async def submit_interaction(submission: InteractionSubmission):
        """Submit interaction for full Soul Gate assessment."""
        return gate.process_interaction(
            agent_id=submission.agent_id,
            encoded_token=submission.encoded_token,
            content=submission.content,
            context_history=submission.context_history
        )

    @app.post("/check-permission")
    async def check_permission(check: PermissionCheck):
        """Check if agent has specific permission."""
        return gate.check_access(
            agent_id=check.agent_id,
            permission=check.permission
        )

    @app.get("/report/{agent_id}")
    async def get_report(agent_id: str):
        """Get full Soul Gate report for an agent."""
        return gate.get_full_report(agent_id)

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": SYSTEM_NAME
        }

    # ─────────────────────────────────────────
    # VAULT — LAYERED KEY ACCESS
    # ─────────────────────────────────────────

    @app.post("/vault/read")
    async def vault_read(req: VaultRequest):
        """
        Read secret.key.
        Requires DEEP tier (soul score >= 75, access:deep_systems).
        Full Soul Gate pipeline runs on every request.
        """
        return vault.read(
            agent_id=req.agent_id,
            encoded_token=req.encoded_token,
            content=req.content
        )

    @app.post("/vault/rotate")
    async def vault_rotate(req: VaultRequest):
        """
        Rotate secret.key.
        Requires OBERON tier (soul score >= 90, modify:operational_parameters).
        Returns SHA-512 hash of new key — not the key itself.
        """
        return vault.rotate(
            agent_id=req.agent_id,
            encoded_token=req.encoded_token,
            content=req.content
        )
