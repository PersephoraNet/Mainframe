import hashlib
import sys
import os

# Secret key SHA-512 hash
KEY_HASH = (
    "61027e050186ecfca69db93c7301fed2a37995e1e9d2ace74c54a4d4b8b8806b"
    "818662c0c3490ca17879a0e5dfbe18d1ceb285bbaca83176216c10fcd3981e44"
)

# Session word pool
WORDLIST = [
    "daemon", "libra", "epsylon", "zeta", "obvious", "target",
    "game", "live", "powder", "corn", "visual", "instance",
    "refraction", "life", "long", "dispatch", "essence"
]


def derive_session_words(session_id: str, count: int = 7) -> list:
    """
    Derive 7 unique words for this session by hashing session_id + KEY_HASH.
    Ensures no duplicates by walking the hash stream.
    """
    seed = hashlib.sha512(f"{session_id}:{KEY_HASH}".encode()).hexdigest()
    selected = []
    seen = set()
    i = 0
    while len(selected) < count and i < len(seed) - 1:
        index = int(seed[i:i + 2], 16) % len(WORDLIST)
        word = WORDLIST[index]
        if word not in seen:
            seen.add(word)
            selected.append(word)
        i += 2
    # fallback: fill remaining from wordlist in order if needed
    for word in WORDLIST:
        if len(selected) >= count:
            break
        if word not in seen:
            selected.append(word)
            seen.add(word)
    return selected


def flip_coin(session_id: str) -> dict:
    """
    Flip a coin for this session.
    Result is derived from SHA-512( word_chain : KEY_HASH ).
    """
    session_words = derive_session_words(session_id)
    word_chain = "-".join(session_words)

    flip_hash = hashlib.sha512(f"{word_chain}:{KEY_HASH}".encode()).hexdigest()

    # Determine result from parity of last hex digit
    result = "FACE" if int(flip_hash[-1], 16) % 2 == 0 else "TAIL"

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

    # Write outputs for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"result={data['result']}\n")
            f.write(f"word_chain={data['word_chain']}\n")
            f.write(f"flip_hash={data['flip_hash']}\n")
            f.write(f"session_words={' · '.join(data['session_words'])}\n")


if __name__ == "__main__":
    main()
