"""Unit tests for src.filtering (product filter and empty narrative removal)."""
import pandas as pd
import pytest
from src.filtering import filter_products, remove_empty_narratives


def test_filter_products_keeps_only_allowed():
    df = pd.DataFrame({
        "Product": ["Credit card", "Mortgage", "Personal loan", "Credit card"],
        "Consumer complaint narrative": ["a", "b", "c", "d"],
    })
    out = filter_products(df)
    assert len(out) == 3
    assert set(out["Product"].tolist()) == {"Credit card", "Personal loan"}


def test_filter_products_empty_if_none_match():
    df = pd.DataFrame({
        "Product": ["Mortgage", "Debt collection"],
        "Consumer complaint narrative": ["a", "b"],
    })
    out = filter_products(df)
    assert len(out) == 0


def test_remove_empty_narratives_drops_empty():
    df = pd.DataFrame({
        "Product": ["Credit card"] * 4,
        "Consumer complaint narrative": ["", "  ", "valid text", "also valid"],
    })
    out = remove_empty_narratives(df)
    assert len(out) == 2
    assert "valid text" in out["Consumer complaint narrative"].tolist()
