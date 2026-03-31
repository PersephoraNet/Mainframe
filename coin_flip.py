import hashlib
import sys
import os
import json
from datetime import datetime, timezone

from key_hash import SECRET_KEY_HASH as KEY_HASH

WORDLIST = [
    "daemon", "libra", "epsylon", "zeta", "obvious", "target",
    "game", "live", "powder", "corn", "visual", "instance",
    "refraction", "life", "long", "dispatch", "essence"
]

ASCII_FACE = r"""
        . - ~ ~ ~ - .
    , '   F A C E     ' ,
  ,                       ,
 ,    ~~    eyes    ~~     ,
 ,        ^     ^          ,
  ,          . .          ,
    ,      \  ___  /     ,
      ' - , _ _ _ _ , - '
"""

ASCII_TAIL = r"""
        . - ~ ~ ~ - .
    , '   T A I L     ' ,
  ,                       ,
 ,    *   *   *   *   *    ,
 ,      *   *   *   *      ,
  ,    *   *   *   *   *  ,
    ,      *   *   *     ,
      ' - , _ _ _ _ , - '
"""

HISTORY_FILE = "flip_history.json"


def derive_session_words(session_id: str, count: int = 7, key_hash: str = None) -> list:
    kh = key_hash or KEY_HASH
    seed = hashlib.sha512(f"{session_id}:{kh}".encode()).hexdigest()
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


def flip_coin(session_id: str, key_hash: str = None) -> dict:
    kh = key_hash or KEY_HASH
    session_words = derive_session_words(session_id, key_hash=kh)
    word_chain = "-".join(session_words)
    flip_hash = hashlib.sha512(f"{word_chain}:{kh}".encode()).hexdigest()
    result = "FACE" if int(flip_hash[-1], 16) % 2 == 0 else "TAIL"
    return {
        "session_id": session_id,
        "session_words": session_words,
        "word_chain": word_chain,
        "flip_hash": flip_hash,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(data: dict):
    history = load_history()
    history.append({
        "session_id": data["session_id"],
        "timestamp": data["timestamp"],
        "words": data["session_words"],
        "result": data["result"],
        "flip_hash": data["flip_hash"],
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def print_proof(data: dict):
    print("\n--- PROOF OF FAIRNESS ---")
    print("Anyone can verify this result independently:")
    print(f"  1. Word chain : {data['word_chain']}")
    print(f"  2. Key hash   : {KEY_HASH[:32]}...")
    print(f"  3. Run        : sha512( word_chain + ':' + key_hash )")
    print(f"  4. Full hash  : {data['flip_hash']}")
    print(f"  5. Last digit : {data['flip_hash'][-1]}  "
          f"({'even → FACE' if int(data['flip_hash'][-1], 16) % 2 == 0 else 'odd → TAIL'})")
    print("-------------------------\n")


def main():
    args = sys.argv[1:]
    gate_mode = "--gate" in args
    positional = [a for a in args if not a.startswith("--")]

    session_id = os.environ.get("SESSION_ID") or (positional[0] if positional else None)
    if not session_id:
        print("ERROR: No SESSION_ID provided.")
        sys.exit(1)

    key_hash = None
    if gate_mode:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "soul_gate"))
        from api.main import SoulGateOrchestrator
        from vault.flip_gate import FlipGate

        agent_type = os.environ.get("SOUL_GATE_AGENT_TYPE", "human")
        fg = FlipGate(SoulGateOrchestrator())
        gate_result = fg.request(agent_type=agent_type, session_id=session_id)

        print(f"\n  [SOUL GATE]  tier={gate_result['tier']}  "
              f"score={gate_result['soul_score']:.1f}  "
              f"granted={gate_result['granted']}")

        if not gate_result["granted"]:
            print(f"  [SOUL GATE]  DENIED — {gate_result['reason']}")
            sys.exit(1)

        key_hash = gate_result["key_hash"]

    data = flip_coin(session_id, key_hash=key_hash)

    # ASCII art
    print(ASCII_FACE if data["result"] == "FACE" else ASCII_TAIL)

    # Result banner
    divider = "=" * 60
    print(divider)
    print("           COIN FLIP — SESSION RESULT")
    print(divider)
    print(f"  Session ID   : {data['session_id']}")
    print(f"  Timestamp    : {data['timestamp']}")
    print(f"  Session Words: {' · '.join(data['session_words'])}")
    print(f"  Word Chain   : {data['word_chain']}")
    print(divider)
    print(f"  RESULT       : >>> {data['result']} <<<")
    print(divider)

    # Proof of fairness
    print_proof(data)

    # History
    save_history(data)
    history = load_history()
    face_count = sum(1 for h in history if h["result"] == "FACE")
    tail_count = sum(1 for h in history if h["result"] == "TAIL")
    print(f"  All-time: FACE {face_count}  |  TAIL {tail_count}  (total: {len(history)})")

    # GitHub Actions outputs
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"result={data['result']}\n")
            f.write(f"word_chain={data['word_chain']}\n")
            f.write(f"flip_hash={data['flip_hash']}\n")
            f.write(f"session_words={' · '.join(data['session_words'])}\n")
            f.write(f"face_count={face_count}\n")
            f.write(f"tail_count={tail_count}\n")
            f.write(f"total_flips={len(history)}\n")


if __name__ == "__main__":
    main()
