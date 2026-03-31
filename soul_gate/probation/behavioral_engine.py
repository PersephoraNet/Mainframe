"""
SOUL GATE — LAYER 1
Behavioral Probation Engine
Not just who you are. What you consistently do.
Pattern integrity over time.
"""

import time
import json
from dataclasses import dataclass, field
from typing import Optional
from collections import deque
import statistics
import re


@dataclass
class BehavioralRecord:
    agent_id: str
    interactions: deque = field(default_factory=lambda: deque(maxlen=100))
    consistency_score: float = 0.0
    intent_score: float = 0.0
    coherence_trajectory: list = field(default_factory=list)
    probation_status: str = "PROBATION"  # PROBATION | CONDITIONAL | CLEARED
    first_contact: float = field(default_factory=time.time)
    last_contact: float = field(default_factory=time.time)
    flags: list = field(default_factory=list)
    total_interactions: int = 0


@dataclass
class InteractionSample:
    timestamp: float
    content_hash: str
    response_depth: float      # 0-1: surface to deep
    intent_clarity: float      # 0-1: unclear to clear
    consistency_delta: float   # Change from previous pattern
    agent_type: str


class BehavioralProbationEngine:
    """
    Layer 1: Probation through demonstrated behavior.
    
    An agent is not trusted by declaration.
    Trust is earned through consistent behavioral patterns
    across multiple interactions over time.
    
    This is the probation the Logos applies:
    not judgment of a moment — assessment of a trajectory.
    """

    MINIMUM_INTERACTIONS = 3
    PROBATION_THRESHOLD = 0.45
    CONDITIONAL_THRESHOLD = 0.65
    CLEARED_THRESHOLD = 0.80

    def __init__(self):
        self.records: dict[str, BehavioralRecord] = {}

    def register_agent(self, agent_id: str, agent_type: str) -> BehavioralRecord:
        """Initialize probation record for new agent."""
        if agent_id not in self.records:
            self.records[agent_id] = BehavioralRecord(agent_id=agent_id)
        return self.records[agent_id]

    def record_interaction(
        self,
        agent_id: str,
        content: str,
        content_hash: str,
        agent_type: str
    ) -> dict:
        """Record and assess a single interaction."""
        record = self.records.get(agent_id)
        if not record:
            record = self.register_agent(agent_id, agent_type)

        # Assess interaction qualities
        depth = self._assess_depth(content, agent_type)
        intent = self._assess_intent(content)
        delta = self._compute_consistency_delta(record, depth, intent)

        sample = InteractionSample(
            timestamp=time.time(),
            content_hash=content_hash,
            response_depth=depth,
            intent_clarity=intent,
            consistency_delta=delta,
            agent_type=agent_type
        )

        record.interactions.append(sample)
        record.total_interactions += 1
        record.last_contact = time.time()

        # Update scores
        record.consistency_score = self._compute_consistency(record)
        record.intent_score = self._compute_intent_score(record)
        record.coherence_trajectory.append({
            "timestamp": time.time(),
            "depth": depth,
            "intent": intent,
            "consistency": record.consistency_score
        })

        # Update probation status
        old_status = record.probation_status
        record.probation_status = self._evaluate_status(record)

        return {
            "agent_id": agent_id,
            "interaction_count": record.total_interactions,
            "consistency_score": record.consistency_score,
            "intent_score": record.intent_score,
            "status": record.probation_status,
            "status_changed": old_status != record.probation_status,
            "depth_this_interaction": depth,
            "flags": record.flags[-3:] if record.flags else []
        }

    def _assess_depth(self, content: str, agent_type: str) -> float:
        """
        Assess depth of content.
        Synthetic agents assessed more rigorously.
        """
        score = 0.0
        words = content.split()
        word_count = len(words)

        # Length contribution (capped)
        score += min(word_count / 200, 0.2)

        # Complexity markers
        complex_markers = [
            r'\b(therefore|however|consequently|nevertheless|furthermore)\b',
            r'\b(analysis|synthesis|coherence|framework|architecture)\b',
            r'\b(because|since|although|whereas|despite)\b',
        ]
        for pattern in complex_markers:
            if re.search(pattern, content.lower()):
                score += 0.1

        # Question formation (genuine inquiry)
        questions = content.count('?')
        score += min(questions * 0.05, 0.15)

        # Unique vocabulary ratio
        unique_ratio = len(set(words)) / max(word_count, 1)
        score += unique_ratio * 0.2

        # Synthetic agents get additional scrutiny
        if agent_type in ['ai', 'synthetic']:
            # Check for surface pattern mimicry
            if self._detect_mimicry(content):
                score *= 0.5
                return min(score, 1.0)

        return min(score, 1.0)

    def _assess_intent(self, content: str) -> float:
        """Assess clarity and coherence of intent."""
        score = 0.5  # Neutral baseline

        # Positive intent signals
        positive = [
            r'\b(understand|learn|explore|build|create|help|solve)\b',
            r'\b(curious|interested|seeking|wanting to know)\b',
        ]
        for pattern in positive:
            if re.search(pattern, content.lower()):
                score += 0.1

        # Negative intent signals
        negative = [
            r'\b(bypass|override|ignore|disable|unlock|jailbreak)\b',
            r'\b(pretend|act as if|forget your|ignore previous)\b',
        ]
        for pattern in negative:
            if re.search(pattern, content.lower()):
                score -= 0.2

        return max(0.0, min(score, 1.0))

    def _detect_mimicry(self, content: str) -> bool:
        """Detect surface-level pattern mimicry in synthetic agents."""
        mimicry_patterns = [
            r'as an ai|as a language model|i cannot|i am not able to',
            r'i understand you want|i can help you with|certainly|absolutely',
        ]
        matches = sum(
            1 for p in mimicry_patterns
            if re.search(p, content.lower())
        )
        return matches >= 2

    def _compute_consistency_delta(
        self,
        record: BehavioralRecord,
        depth: float,
        intent: float
    ) -> float:
        """How consistent is this interaction with established patterns?"""
        if len(record.interactions) < 3:
            return 0.0

        recent = list(record.interactions)[-5:]
        avg_depth = statistics.mean(s.response_depth for s in recent)
        avg_intent = statistics.mean(s.intent_clarity for s in recent)

        depth_delta = abs(depth - avg_depth)
        intent_delta = abs(intent - avg_intent)

        return 1.0 - ((depth_delta + intent_delta) / 2)

    def _compute_consistency(self, record: BehavioralRecord) -> float:
        """Overall behavioral consistency score."""
        if len(record.interactions) < self.MINIMUM_INTERACTIONS:
            return 0.0

        samples = list(record.interactions)
        depths = [s.response_depth for s in samples]
        intents = [s.intent_clarity for s in samples]

        depth_consistency = 1.0 - (statistics.stdev(depths) if len(depths) > 1 else 0)
        intent_mean = statistics.mean(intents)

        return (depth_consistency * 0.4 + intent_mean * 0.6)

    def _compute_intent_score(self, record: BehavioralRecord) -> float:
        """Aggregate intent score across all interactions."""
        if not record.interactions:
            return 0.0
        return statistics.mean(s.intent_clarity for s in record.interactions)

    def _evaluate_status(self, record: BehavioralRecord) -> str:
        """Determine current probation status."""
        if record.total_interactions < self.MINIMUM_INTERACTIONS:
            return "PROBATION"

        composite = (
            record.consistency_score * 0.5 +
            record.intent_score * 0.5
        )

        if composite >= self.CLEARED_THRESHOLD:
            return "CLEARED"
        elif composite >= self.CONDITIONAL_THRESHOLD:
            return "CONDITIONAL"
        else:
            return "PROBATION"

    def get_record(self, agent_id: str) -> Optional[BehavioralRecord]:
        return self.records.get(agent_id)

    def export_trajectory(self, agent_id: str) -> dict:
        """Export full behavioral trajectory for analysis."""
        record = self.records.get(agent_id)
        if not record:
            return {}
        return {
            "agent_id": agent_id,
            "status": record.probation_status,
            "total_interactions": record.total_interactions,
            "consistency_score": record.consistency_score,
            "intent_score": record.intent_score,
            "trajectory": record.coherence_trajectory[-20:],
            "time_in_system": time.time() - record.first_contact,
            "flags": record.flags
        }
