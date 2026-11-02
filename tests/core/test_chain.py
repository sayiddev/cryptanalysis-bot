import base64

from app.core import chain


def test_auto_chain_decodes_hex_then_base64():
    original = (
        "the quick brown fox jumps over the lazy dog near the riverbank at dawn"
    )
    hex_layer = original.encode().hex()
    b64_layer = base64.b64encode(hex_layer.encode()).decode()

    result = chain.auto_chain(b64_layer)

    assert result.is_plaintext
    assert original in result.final_text
    encodings_used = [step.encoding for step in result.steps]
    assert "base64" in encodings_used
    assert "hex" in encodings_used


def test_auto_chain_decodes_url_encoding():
    original = "security researchers love classic cipher puzzles"
    encoded = original.replace(" ", "%20")

    result = chain.auto_chain(encoded)

    assert result.is_plaintext
    assert "security researchers" in result.final_text


def test_auto_chain_stops_on_already_plaintext_input():
    original = "this text is already plain english and needs no decoding at all"
    result = chain.auto_chain(original)
    assert result.is_plaintext
    assert result.steps == []


def test_auto_chain_does_not_crash_on_random_bytes():
    import os

    random_text = os.urandom(32).hex()  # hex of random bytes, not english after decode
    result = chain.auto_chain(random_text)
    # Should decode the hex layer at least, then stop — must not raise.
    assert isinstance(result.final_text, str)
