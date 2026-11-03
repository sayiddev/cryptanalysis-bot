from app.core import hash_tools


def test_sha256_hex_matches_known_vector():
    assert hash_tools.sha256_hex("") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    assert hash_tools.sha256_hex("hello") == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_sha1_hex_matches_known_vector():
    assert hash_tools.sha1_hex("hello") == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"


def test_md5_hex_matches_known_vector():
    assert hash_tools.md5_hex("hello") == "5d41402abc4b2a76b9719d911017c592"


def test_base64_encode_roundtrips_with_stdlib():
    import base64

    text = "hello world"
    encoded = hash_tools.base64_encode(text)
    assert base64.b64decode(encoded).decode() == text
