from app.core import xor_breaker

PLAINTEXT = (
    "The quick brown fox jumps over the lazy dog. Classic pangrams like this "
    "one are useful for testing cryptographic routines because they contain "
    "a good spread of common English letters and simple punctuation marks. "
) * 6


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def test_guess_key_lengths_finds_true_length():
    key = b"KEY"
    ciphertext = _xor_encrypt(PLAINTEXT.encode(), key)

    guesses = xor_breaker.guess_key_lengths(ciphertext, max_len=10, top_n=3)

    assert len(key) in guesses


def test_crack_repeating_key_xor_recovers_plaintext():
    key = b"LION"
    ciphertext = _xor_encrypt(PLAINTEXT.encode(), key)

    results = xor_breaker.crack_repeating_key_xor(ciphertext, max_key_len=10, candidates=3)

    assert results
    best = results[0]
    assert best.plaintext == PLAINTEXT
    # A multiple of the true key length (e.g. "LIONLION") decrypts just as
    # correctly as the minimal-period key, so only the period must divide evenly.
    assert best.key_length % len(key) == 0
