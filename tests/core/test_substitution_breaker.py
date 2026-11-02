import random
import string

from app.core import scoring, substitution_breaker

# Pulled from the local corpus so the quadgram model has strong signal on it.
PLAINTEXT = (
    "The history of cryptography stretches back thousands of years long before "
    "computers existed to help with calculations ancient rulers needed a way to "
    "send messages that enemies could not read if the messenger was captured"
)


def _random_substitution_cipher(text: str, seed: int = 42) -> str:
    rng = random.Random(seed)
    letters = list(string.ascii_uppercase)
    shuffled = letters[:]
    rng.shuffle(shuffled)
    mapping = dict(zip(letters, shuffled))
    out = []
    for ch in text:
        if ch.isalpha():
            mapped = mapping[ch.upper()]
            out.append(mapped if ch.isupper() else mapped.lower())
        else:
            out.append(ch)
    return "".join(out)


def test_crack_substitution_improves_on_ciphertext_and_mostly_recovers_text():
    ciphertext = _random_substitution_cipher(PLAINTEXT)

    result = substitution_breaker.crack_substitution(ciphertext, restarts=6, iterations=1500)

    ciphertext_score = scoring.quadgram_log_score(ciphertext)
    assert result.score > ciphertext_score  # decoded text scores better than ciphertext

    original_letters = scoring.clean_letters(PLAINTEXT)
    recovered_letters = scoring.clean_letters(result.plaintext)
    assert len(original_letters) == len(recovered_letters)

    matches = sum(1 for a, b in zip(original_letters, recovered_letters) if a == b)
    accuracy = matches / len(original_letters)
    assert accuracy >= 0.6, f"only {accuracy:.0%} of letters recovered correctly"
