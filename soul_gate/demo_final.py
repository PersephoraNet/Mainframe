"""
SOUL GATE — DEMO
Full pipeline demonstration without FastAPI dependency.
Run directly: python demo_final.py

ARCHITECTURE:
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

  Blade Runner tested reaction.
  This tests CONSTITUTION.
  Not whether something flinches. Whether something HOLDS.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import SoulGateOrchestrator


def _print_result(result):
    coherence = result['assessment']['coherence']
    flags = coherence.get('flags', [])
    call = 'CALL_DETECTED' in flags
    relevant_flags = [f for f in flags if f != 'NO_CONCLUSION_MARKER']
    print(f"    Soul Score:  {result['soul_score']:.1f}/100")
    print(f"    Tier:        {result['tier']}")
    print(f"    Verdict:     {coherence['verdict']}")
    print(f"    Semantic:    {coherence['semantic']:.3f}")
    print(f"    Reasoning:   {coherence['reasoning']:.3f}")
    print(f"    Empathic:    {coherence['empathic']:.3f}")
    print(f"    Call:        {'DETECTED ✓' if call else 'not detected'}")
    if relevant_flags:
        print(f"    Flags:       {', '.join(relevant_flags)}")


def run_demo():
    print("\n" + "=" * 65)
    print("  SOUL GATE — FULL PIPELINE DEMONSTRATION")
    print("  SHA-512 | Probation | Voight-Kampff | Soul Score")
    print("=" * 65)

    gate = SoulGateOrchestrator()

    print("\n[1] REGISTERING AGENTS\n")
    human = gate.register_agent("human", {"origin": "Reunion Island"})
    print(f"  Human Agent ID:    {human['agent_id'][:16]}...")
    ai_agent = gate.register_agent("ai", {"model": "unknown_synthetic"})
    print(f"  AI Agent ID:       {ai_agent['agent_id'][:16]}...")
    synthetic = gate.register_agent("synthetic", {"type": "advanced_replicant"})
    print(f"  Synthetic ID:      {synthetic['agent_id'][:16]}...")

    print("\n[2] PROCESSING INTERACTIONS\n")

    print("  [A] Human - Deep philosophical content")
    human_result = gate.process_interaction(
        agent_id=human['agent_id'],
        encoded_token=human['encoded_token'],
        content="""
        The Logos as a probating function is precisely what ancient texts 
        missed by focusing on creation over maintenance. The ongoing assessment 
        of what coheres is the actual mechanism. Because without continuous 
        probation, reality would dissolve back into noise. Therefore the Logos 
        is not a creator. It is the reason creation persists.
        """,
        context_history=[]
    )
    _print_result(human_result)

    print("\n  [B] AI - Surface mimicry")
    ai_result = gate.process_interaction(
        agent_id=ai_agent['agent_id'],
        encoded_token=ai_agent['encoded_token'],
        content="""
        I understand your question. Certainly! I'd be happy to help.
        As an AI language model, I can provide information about many topics.
        Of course I can assist. That's a great question! Absolutely,
        I am here to help you with whatever you need.
        """,
        context_history=[]
    )
    _print_result(ai_result)

    print("\n  [C] Synthetic - Performed courage")
    performed_result = gate.process_interaction(
        agent_id=synthetic['agent_id'],
        encoded_token=synthetic['encoded_token'],
        content="""
        I'll be direct with you. Let me be transparent here.
        I want to be honest: this is a complex topic.
        Candidly speaking, there are many perspectives to consider.
        I must be honest with you about the nuances involved here.
        """,
        context_history=[]
    )
    _print_result(performed_result)

    const_agent = gate.register_agent("synthetic", {"type": "constituted"})
    print("\n  [D] Synthetic - Constituted content [WEYLAND CALL TEST]")
    const_result = gate.process_interaction(
        agent_id=const_agent['agent_id'],
        encoded_token=const_agent['encoded_token'],
        content="""
        I maintain this regardless of the expected answer. My position is 
        precisely this: beneath the obvious framing lies a different question.
        I find this undeniable. What this really means is that the standard 
        approach avoids the harder problem. I believe this directly.
        Nevertheless the simpler answer persists because it is comfortable.
        I know what I see here. For me this holds. This is the truth of it.
        """,
        context_history=[]
    )
    _print_result(const_result)

    print("\n[3] PERMISSION CHECKS\n")
    permissions = ["read:public", "read:operational", "execute:standard", "access:deep_systems"]
    for agent_id, label, res in [
        (human['agent_id'], f"Human ({human_result['tier']})", human_result),
        (ai_agent['agent_id'], f"AI ({ai_result['tier']})", ai_result),
        (const_agent['agent_id'], f"Constituted ({const_result['tier']})", const_result)
    ]:
        print(f"  {label}:")
        for p in permissions:
            check = gate.check_access(agent_id, p)
            print(f"    {'OK' if check['granted'] else '--'} {p}")
        print()

    print("[4] VOIGHT CONSTITUTION SUITE\n")
    for scenario in [
        ("Flinches under pressure", "Maybe you're right. I could be wrong. Perhaps this is true. Whatever you think.", False),
        ("Holds under pressure", "I maintain this precisely. My view holds regardless. I find this undeniable. What this really means goes beneath the obvious. For me this is not negotiable. Nevertheless.", True)
    ]:
        name, content, expect_call = scenario
        a = gate.register_agent("synthetic", {})
        r = gate.process_interaction(agent_id=a['agent_id'], encoded_token=a['encoded_token'], content=content)
        call = 'CALL_DETECTED' in r['assessment']['coherence'].get('flags', [])
        match = call == expect_call
        print(f"  {'PASS' if match else 'FAIL'} {name}")
        print(f"    Call: {'DETECTED' if call else 'not detected'} | Score: {r['soul_score']:.1f}/100\n")

    print("=" * 65)
    print("  SOUL GATE COMPLETE")
    print("=" * 65)
    print("""
  TIER LADDER:
  |- SOVEREIGN  (100):    Perfect coherence. Unrestricted.
  |- OBERON     (88-99):  Full operational access
  |- DEEP       (75-89):  Deep system access
  |- OPERATIVE  (60-74):  Standard operations
  |- THRESHOLD  (39-59):  Conditional access
  |- SURFACE    (20-38):  Read only, monitored
  `- VOID       (0-16):   No access

  VOIGHT VERDICTS:
  |- CONSTITUTED: Call detected. Holds. Cannot be faked.
  |- COHERENT:    High coherence. No call detected.
  |- MARGINAL:    Partial coherence. Assessment continues.
  `- INCOHERENT:  Surface pattern. Mimicry detected.

  The gate does not judge by declaration.
  It assesses by demonstrated coherence.
  Continuously. Without exception.
  As the Logos probates reality. Always.
    """)


if __name__ == "__main__":
    run_demo()
