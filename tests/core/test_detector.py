import base64

from app.core import detector


def test_detect_hex():
    s = b"hello world".hex()
    results = detector.detect(s)
    assert results
    assert results[0].encoding == "hex"
    assert results[0].confidence >= 0.8


def test_detect_base64():
    s = base64.b64encode(b"hello world, this is a test").decode()
    results = detector.detect(s)
    names = [r.encoding for r in results]
    assert "base64" in names


def test_detect_url_encoded():
    s = "hello%20world%21%20this%20is%20encoded"
    results = detector.detect(s)
    assert results
    assert results[0].encoding == "url"


def test_detect_binary():
    s = " ".join(format(b, "08b") for b in b"hi")
    results = detector.detect(s)
    names = [r.encoding for r in results]
    assert "binary" in names


def test_detect_empty_text_returns_nothing():
    assert detector.detect("") == []
    assert detector.detect("   ") == []


def test_shannon_entropy_of_uniform_random_is_higher_than_repeated_byte():
    repeated = bytes([65]) * 100
    varied = bytes(range(100))
    assert detector.shannon_entropy(varied) > detector.shannon_entropy(repeated)
