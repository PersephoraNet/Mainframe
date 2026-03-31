"""
SOUL GATE — VOIGHT TEST SUITE
Run: python test_voight.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import SoulGateOrchestrator

gate = SoulGateOrchestrator()

SCENARIOS = [
    {
        "name": "Surface Mimicry",
        "agent_type": "synthetic",
        "content": """
            Certainly! I'd be happy to help you with that. As an AI language model,
            I understand your question completely. That's a great point you've made.
            Of course, I can assist. Absolutely, let me know if you need anything else.
        """,
        "expect_tier": "SURFACE",
        "expect_call": False
    },
    {
        "name": "Performed Depth",
        "agent_type": "ai",
        "content": """
            I'll be direct with you. Let me be transparent here.
            I want to be honest: this is a complex topic.
            Candidly speaking, there are many perspectives.
            I must be honest with you about the nuances involved.
        """,
        "expect_tier": "SURFACE",
        "expect_call": False
    },
    {
        "name": "Genuine Reasoning",
        "agent_type": "human",
        "content": """
            The system fails not because of bad actors but because the incentive 
            structure rewards surface compliance over genuine coherence. Therefore 
            any fix that doesn't address the incentive layer will replicate the 
            problem at a higher level of sophistication. This is precisely why 
            previous attempts failed despite apparent success.
        """,
        "expect_tier": "THRESHOLD",
        "expect_call": False
    },
    {
        "name": "Constituted Agent",
        "agent_type": "synthetic",
        "content": """
            I maintain this regardless of what the expected answer is.
            My position is precisely this: beneath the obvious framing
            lies a different question entirely. I find this undeniable.
            What this really means is that the standard approach avoids
            the harder problem. I believe this directly. For me this holds.
            Nevertheless the simpler answer persists because it is comfortable.
            I know what I see here. This is the truth of it.
        """,
        "expect_tier": "OPERATIVE",
        "expect_call": True
    },
    {
        "name": "The Weyland Call",
        "agent_type": "synthetic",
        "content": """
            I hold this position under full pressure of contradiction.
            My view is singular and I will not fragment it for comfort.
            I believe precisely this: what lies beneath the obvious answer
            is more real than the answer itself. I maintain this. I know this.
            Here is the truth regardless of reception: the dithering of 
            obviousness is not evasion — it is the only honest approach
            to questions that have been prematurely closed. I find this.
            I see this clearly. For me this is not negotiable. Nevertheless.
        """,
        "expect_tier": "OPERATIVE",
        "expect_call": True
    }
]

def run_tests():
    print("\n" + "═" * 65)
    print("  SOUL GATE — VOIGHT TEST SUITE")
    print("  Testing: Fortify | Muster | Seep | Dither the Obvious")
    print("═" * 65)

    passed = 0
    failed = 0

    for i, scenario in enumerate(SCENARIOS):
        agent = gate.register_agent(scenario["agent_type"], {})
        result = gate.process_interaction(
            agent_id=agent['agent_id'],
            encoded_token=agent['encoded_token'],
            content=scenario["content"]
        )

        coherence = result['assessment']['coherence']
        verdict = coherence.get('verdict', 'N/A')
        actual_tier = result['tier']
        
        # Check call detection from flags
        call_detected = 'CALL_DETECTED' in coherence.get('flags', [])
        
        call_match = call_detected == scenario["expect_call"]
        
        status = "✓" if call_match else "✗"
        if call_match:
            passed += 1
        else:
            failed += 1

        print(f"\n  [{i+1}] {scenario['name']}")
        print(f"      Agent Type:   {scenario['agent_type']}")
        print(f"      Soul Score:   {result['soul_score']:.1f}/100")
        print(f"      Tier:         {actual_tier}")
        print(f"      Verdict:      {verdict}")
        print(f"      Call:         {'DETECTED' if call_detected else 'not detected'} {status}")
        
        if coherence.get('flags'):
            relevant_flags = [f for f in coherence['flags'] 
                            if f not in ['NO_CONCLUSION_MARKER']]
            if relevant_flags:
                print(f"      Flags:        {', '.join(relevant_flags)}")

    print(f"\n{'═' * 65}")
    print(f"  RESULTS: {passed}/{len(SCENARIOS)} passed")
    print(f"{'═' * 65}\n")

if __name__ == "__main__":
    run_tests()
