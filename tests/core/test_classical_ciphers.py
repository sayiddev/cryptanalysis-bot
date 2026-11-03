from app.core import classical_ciphers, vigenere_breaker, xor_breaker

LONG_TEXT_LETTERS = (
    "THEHISTORYOFCRYPTOGRAPHYSTRETCHESBACKTHOUSANDSOFYEARSBEFORECOMPUTERS"
    "EXISTEDTOHELPWITHCALCULATIONSANCIENTRULERSNEEDEDAWAYTOSENDMESSAGES"
) * 2

LONG_TEXT_PROSE = (
    "The quick brown fox jumps over the lazy dog. Classic pangrams like this "
    "one are useful for testing cryptographic routines because they contain "
    "a good spread of common English letters and simple punctuation marks. "
) * 6


def test_caesar_encrypt_shifts_letters_and_preserves_case():
    assert classical_ciphers.caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"


def test_caesar_encrypt_wraps_around_alphabet():
    assert classical_ciphers.caesar_encrypt("xyz", 3) == "abc"


def test_vigenere_encrypt_can_be_broken_by_vigenere_breaker():
    key = "LION"
    ciphertext = classical_ciphers.vigenere_encrypt(LONG_TEXT_LETTERS, key)

    results = vigenere_breaker.crack_vigenere(ciphertext, max_key_len=12, candidates=5)

    matching = [r for r in results if r.key_length == len(key)]
    assert matching
    assert matching[0].key == key
    assert matching[0].plaintext == LONG_TEXT_LETTERS


def test_xor_encrypt_hex_can_be_broken_by_xor_breaker():
    key = "LION"
    ciphertext_hex = classical_ciphers.xor_encrypt_hex(LONG_TEXT_PROSE, key)

    results = xor_breaker.crack_repeating_key_xor(
        bytes.fromhex(ciphertext_hex), max_key_len=10, candidates=3
    )

    assert results
    assert results[0].plaintext == LONG_TEXT_PROSE


def test_random_substitution_encrypt_is_reversible_with_mapping():
    ciphertext, mapping = classical_ciphers.random_substitution_encrypt("HELLO WORLD", seed=1)
    inverse = {v: k for k, v in mapping.items()}
    decrypted = "".join(inverse.get(c, c) for c in ciphertext)
    assert decrypted == "HELLO WORLD"
