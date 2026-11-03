from app.core import affine_breaker

PLAINTEXT = (
    "The history of cryptography stretches back thousands of years long before "
    "computers existed to help with calculations ancient rulers needed a way to "
    "send messages that enemies could not read if the messenger was captured"
)


def test_encrypt_decrypt_roundtrip():
    ciphertext = affine_breaker.affine_encrypt(PLAINTEXT, a=5, b=8)
    assert affine_breaker.affine_decrypt(ciphertext, a=5, b=8) == PLAINTEXT


def test_encrypt_rejects_non_coprime_a():
    try:
        affine_breaker.affine_encrypt("hello", a=2, b=1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_crack_affine_recovers_key_and_plaintext():
    ciphertext = affine_breaker.affine_encrypt(PLAINTEXT, a=5, b=8)
    results = affine_breaker.crack_affine(ciphertext, candidates=3)
    assert results
    best = results[0]
    assert best.a == 5
    assert best.b == 8
    assert best.plaintext == PLAINTEXT
