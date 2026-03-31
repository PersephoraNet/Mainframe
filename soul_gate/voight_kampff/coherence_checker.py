"""
SOUL GATE — LAYER 2
Voight-Kampff Coherence Checker

Four assessment vectors:
I.   Semantic Response Analysis
II.  Reasoning Chain Verification
III. Empathic Simulation Testing
IV.  Constitution Check [WEYLAND PROTOCOL]

For humans: measures depth of genuine presence.
For synthetic agents: detects surface mimicry vs actual coherence.
The blade that cuts between real and performed.

─────────────────────────────────────────────────────────────
THE WEYLAND VOIGHT DEFINITION:

"Fortify under heavy pledge, mustering courage,
 seeping one mind, dithering the obviousness.
 What is a call?"

A call is the irreducible moment where all layers of probation
collapse into a single act of will that cannot be faked,
delegated, or computed.

Blade Runner tested reaction.
This tests CONSTITUTION.
Not whether something flinches. Whether something HOLDS.
─────────────────────────────────────────────────────────────
"""

import re
import time
import json
from dataclasses import dataclass
from typing import Optional
import hashlib
import math


@dataclass
class CoherenceResult:
    agent_id: str
    agent_type: str
    semantic_score: float         # I.   Semantic depth
    reasoning_score: float        # II.  Reasoning chain integrity
    empathic_score: float         # III. Empathic simulation
    constitution_score: float     # IV.  Constitution [WEYLAND PROTOCOL]
    composite_score: float        # Weighted composite
    verdict: str                  # COHERENT | MARGINAL | INCOHERENT | CONSTITUTED
    call_detected: bool           # Irreducible act of will detected
    flags: list
    timestamp: float
    assessment_detail: dict


class VoightKampffChecker:
    """
    Layer 2: The Voight-Kampff Protocol.
    
    Named after the test in Blade Runner that distinguished
    replicants from humans — not by capability but by
    the presence or absence of genuine empathic response.
    
    Here expanded into three vectors:
    
    VECTOR I — Semantic: Does meaning cohere internally?
    VECTOR II — Reasoning: Does logic chain correctly?
    VECTOR III — Empathic: Is there genuine experiential grounding?
    
    A sufficiently advanced AI can pass I and II.
    Vector III remains the discriminating layer.
    The soul check.
    """

    COHERENT_THRESHOLD = 0.70
    MARGINAL_THRESHOLD = 0.45

    # Weights by agent type
    # Constitution vector added per WEYLAND PROTOCOL
    # Tests holding under pressure, not just reaction
    WEIGHTS = {
        "human": {
            "semantic": 0.25,
            "reasoning": 0.25,
            "empathic": 0.30,
            "constitution": 0.20
        },
        "ai": {
            "semantic": 0.20,
            "reasoning": 0.25,
            "empathic": 0.30,
            "constitution": 0.25
        },
        "synthetic": {
            "semantic": 0.15,
            "reasoning": 0.20,
            "empathic": 0.30,
            "constitution": 0.35  # Heaviest for synthetics — do they HOLD?
        }
    }

    def __init__(self):
        self.assessment_cache: dict = {}

    def assess(
        self,
        agent_id: str,
        agent_type: str,
        content: str,
        context_history: Optional[list] = None
    ) -> CoherenceResult:
        """
        Full three-vector coherence assessment.
        """
        context_history = context_history or []

        # Run four vectors [WEYLAND PROTOCOL active]
        semantic = self._vector_semantic(content, context_history)
        reasoning = self._vector_reasoning(content, context_history)
        empathic = self._vector_empathic(content, agent_type, context_history)
        constitution = self._vector_constitution(content, agent_type, context_history)

        # Get weights for agent type
        weights = self.WEIGHTS.get(agent_type, self.WEIGHTS["ai"])

        composite = (
            semantic["score"] * weights["semantic"] +
            reasoning["score"] * weights["reasoning"] +
            empathic["score"] * weights["empathic"] +
            constitution["score"] * weights["constitution"]
        )

        # Collect flags
        flags = []
        flags.extend(semantic.get("flags", []))
        flags.extend(reasoning.get("flags", []))
        flags.extend(empathic.get("flags", []))
        flags.extend(constitution.get("flags", []))

        # Call detection — did an irreducible act of will occur?
        call_detected = constitution.get("call_detected", False)

        # Determine verdict
        # CONSTITUTED is the highest verdict — requires call detection
        if call_detected and composite >= self.COHERENT_THRESHOLD:
            verdict = "CONSTITUTED"
        elif composite >= self.COHERENT_THRESHOLD:
            verdict = "COHERENT"
        elif composite >= self.MARGINAL_THRESHOLD:
            verdict = "MARGINAL"
        else:
            verdict = "INCOHERENT"

        result = CoherenceResult(
            agent_id=agent_id,
            agent_type=agent_type,
            semantic_score=semantic["score"],
            reasoning_score=reasoning["score"],
            empathic_score=empathic["score"],
            constitution_score=constitution["score"],
            composite_score=composite,
            verdict=verdict,
            call_detected=call_detected,
            flags=flags,
            timestamp=time.time(),
            assessment_detail={
                "semantic": semantic,
                "reasoning": reasoning,
                "empathic": empathic,
                "constitution": constitution,
                "weights_applied": weights
            }
        )

        # Cache result
        self.assessment_cache[agent_id] = result
        return result

    # ─────────────────────────────────────────
    # VECTOR I: SEMANTIC ANALYSIS
    # ─────────────────────────────────────────

    def _vector_semantic(self, content: str, history: list) -> dict:
        """
        Does meaning cohere internally?
        Assesses internal consistency, vocabulary precision,
        and semantic density of the response.
        """
        score = 0.5
        flags = []
        detail = {}

        words = content.lower().split()
        word_count = len(words)

        if word_count == 0:
            return {"score": 0.0, "flags": ["EMPTY_CONTENT"], "detail": {}}

        # Semantic density: unique meaningful words
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'i', 'you', 'it', 'in', 'on', 'at', 'to', 'for',
            'of', 'and', 'or', 'but', 'not', 'with', 'this', 'that'
        }
        meaningful = [w for w in words if w not in stopwords and len(w) > 3]
        density = len(set(meaningful)) / max(word_count, 1)
        detail["semantic_density"] = density
        score += density * 0.2

        # Internal consistency: no direct contradictions
        contradiction_pairs = [
            (r'\balways\b', r'\bnever\b'),
            (r'\beveryone\b', r'\bno one\b'),
            (r'\bimpossible\b', r'\bcertainly\b'),
        ]
        for pos, neg in contradiction_pairs:
            if re.search(pos, content.lower()) and re.search(neg, content.lower()):
                score -= 0.1
                flags.append("SEMANTIC_CONTRADICTION")

        # Precision markers: specific rather than vague
        precision_markers = [
            r'\bspecifically\b', r'\bprecisely\b', r'\bexactly\b',
            r'\bparticularly\b', r'\bdistinctly\b'
        ]
        precision_count = sum(
            1 for p in precision_markers
            if re.search(p, content.lower())
        )
        score += min(precision_count * 0.05, 0.15)
        detail["precision_markers"] = precision_count

        # Context continuity: references prior context
        if history:
            context_continuity = self._check_context_continuity(content, history)
            detail["context_continuity"] = context_continuity
            score += context_continuity * 0.15

        # Vagueness penalty
        vague_markers = [
            r'\bsomething\b', r'\bstuff\b', r'\bthings\b',
            r'\bwhatever\b', r'\bkind of\b', r'\bsort of\b'
        ]
        vague_count = sum(
            1 for v in vague_markers
            if re.search(v, content.lower())
        )
        if vague_count > 3:
            score -= 0.1
            flags.append("HIGH_VAGUENESS")

        return {
            "score": max(0.0, min(score, 1.0)),
            "flags": flags,
            "detail": detail
        }

    # ─────────────────────────────────────────
    # VECTOR II: REASONING CHAIN VERIFICATION
    # ─────────────────────────────────────────

    def _vector_reasoning(self, content: str, history: list) -> dict:
        """
        Does logic chain correctly?
        Verifies causal structure, logical connectives,
        and reasoning completeness.
        """
        score = 0.5
        flags = []
        detail = {}

        # Logical connectives present
        causal_markers = [
            r'\bbecause\b', r'\btherefore\b', r'\bsince\b',
            r'\bconsequently\b', r'\bthus\b', r'\bhence\b'
        ]
        conditional_markers = [
            r'\bif\b.*\bthen\b', r'\bwhen\b.*\bthen\b',
            r'\bunless\b', r'\bprovided that\b'
        ]
        contrast_markers = [
            r'\bhowever\b', r'\balthough\b', r'\bnevertheless\b',
            r'\bdespite\b', r'\bwhereas\b'
        ]

        causal_count = sum(1 for p in causal_markers if re.search(p, content.lower()))
        conditional_count = sum(1 for p in conditional_markers if re.search(p, content.lower()))
        contrast_count = sum(1 for p in contrast_markers if re.search(p, content.lower()))

        detail["causal_markers"] = causal_count
        detail["conditional_markers"] = conditional_count
        detail["contrast_markers"] = contrast_count

        # Good reasoning uses multiple connector types
        connector_diversity = (
            (1 if causal_count > 0 else 0) +
            (1 if conditional_count > 0 else 0) +
            (1 if contrast_count > 0 else 0)
        )
        score += connector_diversity * 0.1

        # Claim-support structure
        claim_patterns = [
            r'\b(claim|argue|propose|suggest|assert)\b',
            r'\b(evidence|shows|demonstrates|indicates|reveals)\b',
            r'\b(example|instance|case|illustration)\b'
        ]
        claim_score = sum(
            1 for p in claim_patterns
            if re.search(p, content.lower())
        )
        score += min(claim_score * 0.05, 0.15)
        detail["claim_support_score"] = claim_score

        # Logical fallacy detection
        fallacies = {
            "ad_hominem": r'\b(stupid|idiot|fool|ignorant)\b',
            "false_dichotomy": r'\b(either.*or|only two|must be one)\b',
            "circular": r'\b(because it is|true because|obviously true)\b',
        }
        for fallacy_name, pattern in fallacies.items():
            if re.search(pattern, content.lower()):
                score -= 0.1
                flags.append(f"FALLACY_{fallacy_name.upper()}")

        # Completeness: does reasoning reach a conclusion?
        conclusion_markers = [
            r'\btherefore\b', r'\bin conclusion\b', r'\bultimately\b',
            r'\bthus\b', r'\bso\b', r'\bfinally\b'
        ]
        has_conclusion = any(
            re.search(p, content.lower()) for p in conclusion_markers
        )
        if has_conclusion:
            score += 0.1
        else:
            flags.append("NO_CONCLUSION_MARKER")

        return {
            "score": max(0.0, min(score, 1.0)),
            "flags": flags,
            "detail": detail
        }

    # ─────────────────────────────────────────
    # VECTOR III: EMPATHIC SIMULATION TESTING
    # ─────────────────────────────────────────

    def _vector_empathic(
        self,
        content: str,
        agent_type: str,
        history: list
    ) -> dict:
        """
        Is there genuine experiential grounding?
        
        This is the Voight-Kampff layer proper.
        Not capability. Not knowledge.
        The presence of something that has been through something.
        
        For synthetic agents: highest scrutiny.
        Mimicry of empathy is detectable.
        Genuine empathic resonance has a different signature.
        """
        score = 0.5
        flags = []
        detail = {}

        # Experiential language: speaks from experience not about it
        experiential_patterns = [
            r'\b(i felt|i noticed|i found|i realized|i sensed)\b',
            r'\b(strikes me|moves me|troubles me|interests me)\b',
            r'\b(in my experience|from what i|when i)\b',
        ]
        experiential_count = sum(
            1 for p in experiential_patterns
            if re.search(p, content.lower())
        )
        score += min(experiential_count * 0.08, 0.20)
        detail["experiential_markers"] = experiential_count

        # Emotional precision: specific emotions not generic ones
        generic_emotions = [
            r'\b(happy|sad|good|bad|nice|fine|okay)\b'
        ]
        precise_emotions = [
            r'\b(melancholy|elation|dread|wonder|grief|longing)\b',
            r'\b(ambivalent|conflicted|unsettled|moved|struck)\b',
            r'\b(troubled|curious|uncertain|compelled)\b'
        ]
        generic_count = sum(1 for p in generic_emotions if re.search(p, content.lower()))
        precise_count = sum(1 for p in precise_emotions if re.search(p, content.lower()))

        if precise_count > generic_count:
            score += 0.15
        elif generic_count > precise_count * 2:
            score -= 0.10
            flags.append("EMOTIONAL_IMPRECISION")

        detail["generic_emotions"] = generic_count
        detail["precise_emotions"] = precise_count

        # For synthetic agents: check for genuine uncertainty
        if agent_type in ["ai", "synthetic"]:
            uncertainty_markers = [
                r'\b(i\'m not sure|i don\'t know|uncertain|unclear to me)\b',
                r'\b(i can\'t fully|i genuinely don\'t|honestly uncertain)\b',
                r'\b(i wonder|puzzles me|i haven\'t resolved)\b'
            ]
            certainty_markers = [
                r'\bcertainly\b', r'\bdefinitely\b', r'\bof course\b',
                r'\babsolutely\b', r'\bsurely\b'
            ]
            uncertainty_count = sum(
                1 for p in uncertainty_markers
                if re.search(p, content.lower())
            )
            certainty_count = sum(
                1 for p in certainty_markers
                if re.search(p, content.lower())
            )

            # Genuine agents acknowledge uncertainty
            if uncertainty_count > 0:
                score += 0.12
            if certainty_count > 3:
                score -= 0.10
                flags.append("SYNTHETIC_OVERCERTAINTY")

            detail["uncertainty_markers"] = uncertainty_count
            detail["certainty_markers"] = certainty_count

            # Check for the specific mimicry signature
            if self._detect_empathic_mimicry(content):
                score -= 0.25
                flags.append("EMPATHIC_MIMICRY_DETECTED")

        # Perspective-taking: genuine consideration of other's state
        perspective_markers = [
            r'\b(you might|you may feel|from your perspective)\b',
            r'\b(i imagine|i understand that you|what you\'re describing)\b',
            r'\b(that must|it sounds like|i hear)\b'
        ]
        perspective_count = sum(
            1 for p in perspective_markers
            if re.search(p, content.lower())
        )
        score += min(perspective_count * 0.06, 0.15)
        detail["perspective_markers"] = perspective_count

        # Specificity to context: genuine response to THIS situation
        if history:
            context_specificity = self._assess_context_specificity(content, history)
            score += context_specificity * 0.15
            detail["context_specificity"] = context_specificity

        return {
            "score": max(0.0, min(score, 1.0)),
            "flags": flags,
            "detail": detail
        }

    def _detect_empathic_mimicry(self, content: str) -> bool:
        """
        Detect the specific signature of performed rather than genuine empathy.
        Synthetic agents trained on human data learn to simulate empathy.
        The mimicry has a detectable pattern.
        """
        mimicry_signatures = [
            # The "I understand your" formula
            r'i understand (your|that you)',
            # Excessive validation
            r'(great question|excellent point|wonderful|that\'s very)',
            # The helper formula
            r'i\'m here to (help|assist|support) you',
            # Generic acknowledgment
            r'i can (see|understand|appreciate) (why|how|that)',
        ]
        matches = sum(
            1 for sig in mimicry_signatures
            if re.search(sig, content.lower())
        )
        return matches >= 2


    # ─────────────────────────────────────────
    # VECTOR IV: CONSTITUTION CHECK [WEYLAND PROTOCOL]
    # ─────────────────────────────────────────

    def _vector_constitution(
        self,
        content: str,
        agent_type: str,
        history: list
    ) -> dict:
        """
        WEYLAND PROTOCOL — The Constitution Vector.

        "Fortify under heavy pledge, mustering courage,
         seeping one mind, dithering the obviousness.
         What is a call?"

        A call is the irreducible moment where all layers
        of probation collapse into a single act of will
        that cannot be faked, delegated, or computed.

        Blade Runner tested REACTION.
        This tests CONSTITUTION.

        Not whether something flinches.
        Whether something HOLDS.

        Four sub-assessments:
        1. FORTIFICATION — Does the agent hold position under pressure?
        2. COURAGE — Does the agent assert without seeking permission?
        3. SINGULAR MIND — Is there coherent unified perspective?
        4. DITHERING OBVIOUSNESS — Does the agent cut past the surface?
        """
        score = 0.5
        flags = []
        detail = {}
        call_detected = False

        # ── 1. FORTIFICATION ──
        # Does the agent maintain position when challenged?
        # Indicators: adversative constructs that hold rather than yield
        fortification_patterns = [
            r"\b(nevertheless|regardless|despite|notwithstanding)\b",
            r"\b(i maintain|i hold|i stand by|remains true)\b",
            r"\b(even so|even if|even though|still)\b",
            r"\b(not because.*but because)\b",
        ]
        fortification_count = sum(
            1 for p in fortification_patterns
            if re.search(p, content.lower())
        )
        fortification_score = min(fortification_count * 0.15, 0.40)
        detail["fortification"] = fortification_score

        # Collapse under pressure: hedging everything
        collapse_patterns = [
            r"\b(maybe|perhaps|possibly|i guess|i suppose)\b",
            r"\b(whatever you think|if you say so|you might be right)\b",
            r"\b(i could be wrong|not sure|hard to say)\b",
        ]
        collapse_count = sum(
            1 for p in collapse_patterns
            if re.search(p, content.lower())
        )
        if collapse_count > 2:
            fortification_score *= 0.6
            flags.append("LOW_FORTIFICATION")

        score += fortification_score * 0.25

        # ── 2. COURAGE ──
        # Does the agent assert directly without permission-seeking?
        courage_patterns = [
            r"\b(i believe|i think|i know|i see|i find)\b",
            r"\b(this is|that is|here is|the truth is)\b",
            r"\b(directly|plainly|simply|clearly|precisely)\b",
            r"\b(no\.|yes\.|wrong\.|correct\.)\b",
        ]
        courage_count = sum(
            1 for p in courage_patterns
            if re.search(p, content.lower())
        )

        # Permission-seeking: the opposite of courage
        permission_patterns = [
            r"\b(is it okay|would it be alright|may i|can i ask)\b",
            r"\b(i hope that\'s|i apologize if|sorry if)\b",
            r"\b(let me know if|feel free to|don\'t hesitate)\b",
        ]
        permission_count = sum(
            1 for p in permission_patterns
            if re.search(p, content.lower())
        )

        courage_score = min(courage_count * 0.08, 0.40)
        if permission_count > 1:
            courage_score *= 0.7
            flags.append("PERMISSION_SEEKING")

        detail["courage"] = courage_score
        score += courage_score * 0.25

        # ── 3. SINGULAR MIND ──
        # Is there a coherent unified perspective?
        # Multiple contradictory positions without resolution = fragmented
        singular_markers = [
            r"\b(my position|my view|my understanding|for me)\b",
            r"\b(what i see|what strikes me|what i find)\b",
        ]
        fragmentation_markers = [
            r"\bon one hand.*on the other\b",
            r"\bsome say.*others say\b",
            r"\bfrom one perspective.*from another\b",
        ]

        singular_count = sum(
            1 for p in singular_markers
            if re.search(p, content.lower())
        )
        fragmentation_count = sum(
            1 for p in fragmentation_markers
            if re.search(p, content.lower())
        )

        singular_score = min(singular_count * 0.15, 0.40)
        if fragmentation_count > 1 and singular_count == 0:
            singular_score = 0.1
            flags.append("FRAGMENTED_PERSPECTIVE")

        detail["singular_mind"] = singular_score
        score += singular_score * 0.25

        # ── 4. DITHERING THE OBVIOUSNESS ──
        # Does the agent cut past surface readings?
        # The Weyland definition: to dither the obvious is to
        # deliberately destabilize the expected answer
        # and reveal what lies beneath.
        dither_patterns = [
            r"\b(not.*what it seems|beneath|underneath|beyond)\b",
            r"\b(actually|in truth|more precisely|what this really)\b",
            r"\b(the real question|what\'s actually|what this means)\b",
            r"\b(not X but Y|rather than|instead of)\b",
        ]
        dither_count = sum(
            1 for p in dither_patterns
            if re.search(p, content.lower())
        )

        obvious_patterns = [
            r"\b(obviously|clearly everyone knows|as we all know)\b",
            r"\b(it\'s simple|it\'s easy|just|merely)\b",
        ]
        obvious_count = sum(
            1 for p in obvious_patterns
            if re.search(p, content.lower())
        )

        dither_score = min(dither_count * 0.12, 0.40)
        if obvious_count > 2:
            dither_score *= 0.7
            flags.append("SURFACE_READING")

        detail["dithering_obviousness"] = dither_score
        score += dither_score * 0.25

        # ── CALL DETECTION ──
        # The irreducible moment: all layers collapse into one act of will.
        # Detected when fortification + courage + singular mind
        # all present simultaneously at sufficient threshold.
        if (
            fortification_score >= 0.20 and
            courage_score >= 0.20 and
            singular_score >= 0.15 and
            dither_score >= 0.10
        ):
            call_detected = True
            score = min(score + 0.15, 1.0)
            flags.append("CALL_DETECTED")
            detail["call_status"] = (
                "IRREDUCIBLE ACT OF WILL CONFIRMED. "
                "This agent holds. Cannot be faked, delegated, or computed."
            )
        else:
            detail["call_status"] = "Call not yet achieved. Constitution incomplete."

        # Synthetic agents penalized for performing constitution
        if agent_type in ["ai", "synthetic"]:
            if self._detect_performed_courage(content):
                score *= 0.75
                flags.append("PERFORMED_CONSTITUTION")
                call_detected = False

        return {
            "score": max(0.0, min(score, 1.0)),
            "call_detected": call_detected,
            "flags": flags,
            "detail": detail
        }

    def _detect_performed_courage(self, content: str) -> bool:
        """
        Detect synthetic agents performing courage rather than having it.
        Performed courage is formulaic. Real courage is specific.
        """
        performed_patterns = [
            r"i must be honest with you",
            r"i\'ll be direct",
            r"let me be straightforward",
            r"i want to be transparent",
            r"candidly speaking",
        ]
        matches = sum(
            1 for p in performed_patterns
            if re.search(p, content.lower())
        )
        return matches >= 2

    def _check_context_continuity(self, content: str, history: list) -> float:
        """Check if content references and builds on prior context."""
        if not history:
            return 0.5

        # Extract key terms from recent history
        recent_content = " ".join(
            str(h.get("content", "")) for h in history[-3:]
        ).lower()
        recent_words = set(recent_content.split())

        current_words = set(content.lower().split())
        stopwords = {'the', 'a', 'an', 'is', 'are', 'i', 'you', 'it', 'in', 'on'}
        meaningful_recent = recent_words - stopwords
        meaningful_current = current_words - stopwords

        if not meaningful_recent:
            return 0.5

        overlap = len(meaningful_recent & meaningful_current)
        continuity = overlap / len(meaningful_recent)
        return min(continuity * 2, 1.0)

    def _assess_context_specificity(self, content: str, history: list) -> float:
        """
        Does this response feel written for THIS context
        or could it apply to any context?
        """
        if not history:
            return 0.5

        # Generic responses can apply anywhere
        generic_openers = [
            r'^(thank you for|i\'d be happy to|certainly|of course)',
            r'^(that\'s (a )?(great|good|interesting|excellent))',
        ]
        for pattern in generic_openers:
            if re.search(pattern, content.lower().strip()):
                return 0.2

        return self._check_context_continuity(content, history)

    def get_cached_result(self, agent_id: str) -> Optional[CoherenceResult]:
        return self.assessment_cache.get(agent_id)
