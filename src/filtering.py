import pandas as pd

# List of allowed product categories
ALLOWED_PRODUCTS = [
    "Credit card",
    "Personal loan",
    "Savings account",
    "Money transfers"
]

def filter_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only complaints for specified products.
    """
    df_filtered = df[df['Product'].isin(ALLOWED_PRODUCTS)].copy()
    print(f"Filtered products: {len(df_filtered)} rows remain.")
    return df_filtered

def remove_empty_narratives(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove complaints with empty or missing narrative.
    """
    before = len(df)
    df_filtered = df[df['Consumer complaint narrative'].notna() & (df['Consumer complaint narrative'].str.strip() != "")].copy()
    after = len(df_filtered)
    print(f"Removed {before - after} rows with empty narratives.")
    return df_filtered
