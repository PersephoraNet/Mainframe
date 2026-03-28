import hashlib
import sys
import os

# Secret key SHA-512 hash (from key_hash.py)
KEY_HASH = (
    "61027e050186ecfca69db93c7301fed2a37995e1e9d2ace74c54a4d4b8b8806b"
    "818662c0c3490ca17879a0e5dfbe18d1ceb285bbaca83176216c10fcd3981e44"
)

# Session word pool — randomizer source
WORDLIST = [
    "daemon", "libra", "epsylon", "zeta", "obvious", "target",
    "game", "live", "powder", "corn", "visual", "instance",
    "refraction", "life", "long", "dispatch", "essence"
]


def derive_session_words(session_id: str, count: int = 5) -> list:
    """
    Derive a deterministic but unique set of words for this session
    by hashing the session_id against the key hash.
    """
    seed = hashlib.sha512(f"{session_id}:{KEY_HASH}".encode()).hexdigest()
    selected = []
    for i in range(0, count * 2, 2):
        index = int(seed[i:i + 2], 16) % len(WORDLIST)
        selected.append(WORDLIST[index])
    return selected


def flip_coin(session_id: str) -> dict:
    """
    Perform a coin flip for a given session.
    Result is derived from:
      SHA-512( session_words + KEY_HASH )
    """
    session_words = derive_session_words(session_id)
    word_chain = "-".join(session_words)

    flip_input = f"{word_chain}:{KEY_HASH}"
    flip_hash = hashlib.sha512(flip_input.encode()).hexdigest()

    # Determine result from parity of last hex digit
    result = "HEADS" if int(flip_hash[-1], 16) % 2 == 0 else "TAILS"

    return {
        "session_id": session_id,
        "session_words": session_words,
        "word_chain": word_chain,
        "flip_hash": flip_hash,
        "result": result,
    }


def main():
    session_id = os.environ.get("SESSION_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)

    if not session_id:
        print("ERROR: No SESSION_ID provided.")
        sys.exit(1)

    data = flip_coin(session_id)

    divider = "=" * 60
    print(divider)
    print("           COIN FLIP — SESSION RESULT")
    print(divider)
    print(f"  Session ID   : {data['session_id']}")
    print(f"  Session Words: {' · '.join(data['session_words'])}")
    print(f"  Word Chain   : {data['word_chain']}")
    print(f"  Flip Hash    : {data['flip_hash'][:32]}...")
    print(divider)
    print(f"  RESULT       : >>> {data['result']} <<<")
    print(divider)

    # Export result for GitHub Actions downstream steps
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"result={data['result']}\n")
            f.write(f"word_chain={data['word_chain']}\n")
            f.write(f"flip_hash={data['flip_hash']}\n")


if __name__ == "__main__":
    main()
