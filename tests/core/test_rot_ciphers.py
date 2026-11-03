from app.core import rot_ciphers


def test_rot13_is_self_reciprocal():
    text = "Hello, World!"
    once = rot_ciphers.rot13(text)
    twice = rot_ciphers.rot13(once)
    assert once != text
    assert twice == text


def test_rot13_known_value():
    assert rot_ciphers.rot13("hello") == "uryyb"


def test_rot47_is_self_reciprocal():
    text = "Hello, World! 123"
    once = rot_ciphers.rot47(text)
    twice = rot_ciphers.rot47(once)
    assert once != text
    assert twice == text


def test_rot47_leaves_non_printable_untouched():
    assert rot_ciphers.rot47("a\nb") == rot_ciphers.rot47("a") + "\n" + rot_ciphers.rot47("b")
