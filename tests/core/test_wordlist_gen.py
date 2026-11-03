from app.core import wordlist_gen


def test_generate_includes_basic_case_and_year_variants():
    result = wordlist_gen.generate_personal_wordlist(["John"], ["1995"])
    assert "John" in result
    assert "john" in result
    assert "JOHN" in result
    assert "John1995" in result
    assert "1995John" in result
    assert "John95" in result


def test_generate_includes_leetspeak_variant():
    result = wordlist_gen.generate_personal_wordlist(["elsa"], [])
    assert "3l54" in result  # e->3, s->5, a->4


def test_generate_combines_two_words():
    result = wordlist_gen.generate_personal_wordlist(["John", "Max"], [])
    assert "JohnMax" in result
    assert "MaxJohn" in result


def test_generate_respects_max_count():
    result = wordlist_gen.generate_personal_wordlist(["John", "Max", "Smith"], ["1990", "2020"], max_count=20)
    assert len(result) <= 20


def test_generate_ignores_empty_input():
    result = wordlist_gen.generate_personal_wordlist(["", "  "], [""])
    assert result == []
