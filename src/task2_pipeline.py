import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

from config.load_config import load_config, get_project_root
from src.sampling import stratified_sample
from src.chunking import chunk_text
from src.embedding import load_embedding_model
import chromadb


def run_task2():
    cfg = load_config()
    paths = cfg.get("paths", {})
    data_cfg = cfg.get("data", {})
    processed_path = Path(project_root) / paths.get("processed_data", "data/processed/filtered_complaints.csv")
    sample_path = Path(project_root) / paths.get("sample_data", "data/processed/sample_complaints.csv")
    vector_store_path = paths.get("vector_store", "vector_store")
    seed = data_cfg.get("seed", 42)
    sample_size = data_cfg.get("sample_size", 12000)

    print("Loading cleaned dataset...")
    df = pd.read_csv(processed_path)

    print("Creating stratified sample...")
    sample_df = stratified_sample(df, target_size=sample_size, random_state=seed)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(sample_path, index=False)
    print(f"Sample created: {len(sample_df)} complaints")

    print("Loading embedding model...")
    model = load_embedding_model()
    print("Embedding model loaded.")

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=str(Path(project_root) / vector_store_path))
    collection_name = cfg.get("rag", {}).get("collection_name", "complaints")

    try:
        collection = client.get_collection(collection_name)
    except Exception:
        collection = client.create_collection(collection_name)

    print("Chunking, embedding, and indexing...")
    for _, row in tqdm(sample_df.iterrows(), total=len(sample_df)):
        text = row["Consumer complaint narrative"]
        if pd.isna(text) or str(text).strip() == "":
            continue

        chunks = chunk_text(text)
        embeddings = model.encode(chunks)

        for i, emb in enumerate(embeddings):
            collection.add(
                documents=[chunks[i]],
                embeddings=[emb.tolist()],
                metadatas=[{
                    "complaint_id": str(row["Complaint ID"]),
                    "product": str(row["Product"]),
                    "company": str(row["Company"]),
                    "issue": str(row["Issue"]),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }],
                ids=[f"{row['Complaint ID']}_{i}"]
            )

    print(f"Task 2 completed. Vector store saved in '{vector_store_path}/'.")


if __name__ == "__main__":
    run_task2()
