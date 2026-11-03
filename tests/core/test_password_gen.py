import string

from app.core import password_gen


def test_default_length_is_sixteen():
    assert len(password_gen.generate_strong_password()) == 16


def test_length_is_clamped_to_bounds():
    assert len(password_gen.generate_strong_password(4)) == password_gen.MIN_LENGTH
    assert len(password_gen.generate_strong_password(9999)) == password_gen.MAX_LENGTH


def test_contains_all_character_classes():
    pw = password_gen.generate_strong_password(32)
    assert any(c.islower() for c in pw)
    assert any(c.isupper() for c in pw)
    assert any(c.isdigit() for c in pw)
    assert any(c in password_gen._SYMBOLS for c in pw)


def test_passwords_are_not_identical_across_calls():
    passwords = {password_gen.generate_strong_password() for _ in range(20)}
    assert len(passwords) == 20


def test_only_expected_characters_used():
    allowed = set(string.ascii_letters + string.digits + password_gen._SYMBOLS)
    pw = password_gen.generate_strong_password(50)
    assert set(pw) <= allowed
