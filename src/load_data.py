import pandas as pd

def load_data(path: str, chunksize: int = 50000):
    """
    Load CSV as an iterator of chunks (memory-safe).
    """
    print(f"Reading CSV in chunks of {chunksize} rows...")
    return pd.read_csv(
        path,
        chunksize=chunksize,
        low_memory=False
    )
