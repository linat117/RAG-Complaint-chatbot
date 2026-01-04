import sys
from pathlib import Path
import pandas as pd

# Path setup
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

from src.load_data import load_data
from src.filtering import filter_products, remove_empty_narratives
from src.text_cleaning import apply_text_cleaning

def run_pipeline(sample_for_eda: bool = False):
    print("Loading data...")
    reader = load_data("data/raw/complaints.csv")

    processed_chunks = []
    total_rows = 0

    for i, chunk in enumerate(reader, start=1):
        print(f"Processing chunk {i} | Rows: {len(chunk)}")

        # Optional sampling for EDA/debug
        if sample_for_eda and i > 3:
            print("EDA sample mode enabled — stopping early.")
            break

        total_rows += len(chunk)

        # Filtering
        chunk = filter_products(chunk)
        chunk = remove_empty_narratives(chunk)

        if chunk.empty:
            continue

        # Cleaning
        chunk = apply_text_cleaning(chunk)

        processed_chunks.append(chunk)

    print(f"Total rows processed: {total_rows}")

    if not processed_chunks:
        raise ValueError("No data left after filtering.")

    final_df = pd.concat(processed_chunks, ignore_index=True)

    output_path = "data/processed/filtered_complaints.csv"
    final_df.to_csv(output_path, index=False)

    print(f"Saved cleaned dataset to {output_path}")
    print("Task 1 preprocessing completed successfully.")

if __name__ == "__main__":
    run_pipeline(sample_for_eda=True)  # set False for full run
