from app.core import vigenere_breaker

PLAINTEXT_LETTERS = (
    "THEHISTORYOFCRYPTOGRAPHYSTRETCHESBACKTHOUSANDSOFYEARSBEFORECOMPUTERS"
    "EXISTEDTOHELPWITHCALCULATIONSANCIENTRULERSNEEDEDAWAYTOSENDMESSAGES"
    "THATENEMIESCOULDNOTREADIFTHEMESSENGERWASCAPTUREDALONGTHEROAD"
) * 2


def _vigenere_encrypt(plaintext: str, key: str) -> str:
    key = key.upper()
    out = []
    for i, ch in enumerate(plaintext):
        shift = ord(key[i % len(key)]) - ord("A")
        out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
    return "".join(out)


def test_guess_key_lengths_includes_true_length():
    key = "LION"
    ciphertext = _vigenere_encrypt(PLAINTEXT_LETTERS, key)

    guesses = vigenere_breaker.guess_key_lengths(ciphertext, max_len=12, top_n=5)

    assert len(key) in guesses


def test_crack_vigenere_recovers_key_and_plaintext():
    key = "LION"
    ciphertext = _vigenere_encrypt(PLAINTEXT_LETTERS, key)

    results = vigenere_breaker.crack_vigenere(ciphertext, max_key_len=12, candidates=5)

    assert results
    matching = [r for r in results if r.key_length == len(key)]
    assert matching, f"no candidate with key length {len(key)} among {[r.key_length for r in results]}"
    best_match = matching[0]
    assert best_match.key == key
    assert best_match.plaintext == PLAINTEXT_LETTERS
