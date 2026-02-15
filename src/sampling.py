import pandas as pd

def stratified_sample(df: pd.DataFrame, target_size: int = 12000, random_state: int = 42) -> pd.DataFrame:
    samples = []
    product_counts = df["Product"].value_counts(normalize=True)
    for product, proportion in product_counts.items():
        n_samples = int(proportion * target_size)
        product_df = df[df["Product"] == product]
        samples.append(product_df.sample(n=min(n_samples, len(product_df)), random_state=random_state))

    return pd.concat(samples).reset_index(drop=True)
