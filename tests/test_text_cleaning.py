"""Unit tests for src.text_cleaning."""
import pandas as pd
import pytest
from src.text_cleaning import clean_text, apply_text_cleaning


def test_clean_text_lowercase():
    assert clean_text("UPPERCASE") == "uppercase"


def test_clean_text_removes_boilerplate():
    t = clean_text("I am writing to file a complaint about my card.")
    assert "i am writing to file a complaint" not in t
    assert "about" in t or "card" in t


def test_clean_text_returns_empty_for_nan():
    assert clean_text(pd.NA) == ""
    assert clean_text(None) == ""


def test_apply_text_cleaning_adds_cleaned_column():
    df = pd.DataFrame({
        "Consumer complaint narrative": ["Some TEXT here.", "More content"],
    })
    out = apply_text_cleaning(df)
    assert "cleaned_narrative" in out.columns
    assert out["cleaned_narrative"].iloc[0] == "some text here."
