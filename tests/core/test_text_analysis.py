from app.core import text_analysis

ENGLISH_TEXT = (
    "The quick brown fox jumps over the lazy dog near the riverbank at dawn "
    "while security researchers love classic cipher puzzles and statistical analysis."
)


def test_analyze_english_text_looks_english():
    result = text_analysis.analyze_text(ENGLISH_TEXT)
    assert result.looks_english is True
    assert result.letter_count > 0
    assert result.index_of_coincidence > 0
    assert len(result.top_letters) <= 5


def test_analyze_random_letters_does_not_look_english():
    import random
    import string

    rng = random.Random(1)
    random_text = "".join(rng.choice(string.ascii_lowercase) for _ in range(200))
    result = text_analysis.analyze_text(random_text)
    assert result.looks_english is False


def test_analyze_empty_text_does_not_crash():
    result = text_analysis.analyze_text("")
    assert result.letter_count == 0
    assert result.looks_english is False
