import sys
from pathlib import Path
import pandas as pd

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

from config.load_config import load_config, get_project_root
from src.load_data import load_data
from src.filtering import filter_products, remove_empty_narratives
from src.text_cleaning import apply_text_cleaning


def run_pipeline(sample_for_eda: bool = False):
    cfg = load_config()
    paths = cfg.get("paths", {})
    raw_path = Path(project_root) / paths.get("raw_data", "data/raw/complaints.csv")
    output_path = Path(project_root) / paths.get("processed_data", "data/processed/filtered_complaints.csv")
    eda_chunks = cfg.get("data", {}).get("preprocess_eda_chunks", 3)

    print("Loading data...")
    reader = load_data(str(raw_path))

    processed_chunks = []
    total_rows = 0

    for i, chunk in enumerate(reader, start=1):
        print(f"Processing chunk {i} | Rows: {len(chunk)}")

        if sample_for_eda and i > eda_chunks:
            print("EDA sample mode enabled — stopping early.")
            break

        total_rows += len(chunk)
        chunk = filter_products(chunk)
        chunk = remove_empty_narratives(chunk)

        if chunk.empty:
            continue

        chunk = apply_text_cleaning(chunk)
        processed_chunks.append(chunk)

    print(f"Total rows processed: {total_rows}")

    if not processed_chunks:
        raise ValueError("No data left after filtering.")

    final_df = pd.concat(processed_chunks, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"Saved cleaned dataset to {output_path}")
    print("Task 1 preprocessing completed successfully.")


if __name__ == "__main__":
    run_pipeline(sample_for_eda=False)
