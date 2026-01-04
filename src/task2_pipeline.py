import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Project path
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

# Custom modules
from src.sampling import stratified_sample
from src.chunking import chunk_text
from src.embedding import load_embedding_model

# New Chroma imports
import chromadb

def run_task2():
    print("Loading cleaned dataset...")
    df = pd.read_csv("data/processed/filtered_complaints.csv")

    print("Creating stratified sample...")
    sample_df = stratified_sample(df, target_size=12000)
    sample_df.to_csv("data/processed/sample_complaints.csv", index=False)
    print(f"Sample created: {len(sample_df)} complaints")

    print("Loading embedding model...")
    model = load_embedding_model()
    print("Embedding model loaded.")

    print("Initializing ChromaDB...")
    # ✅ New API - using PersistentClient instead of deprecated Settings
    client = chromadb.PersistentClient(path="vector_store")

    # Create or get collection
    try:
        collection = client.get_collection("complaints")
    except:
        collection = client.create_collection("complaints")

    print("Chunking, embedding, and indexing...")
    for _, row in tqdm(sample_df.iterrows(), total=len(sample_df)):
        text = row["Consumer complaint narrative"]
        if pd.isna(text) or text.strip() == "":
            continue

        chunks = chunk_text(text)
        embeddings = model.encode(chunks)

        for i, emb in enumerate(embeddings):
            collection.add(
                documents=[chunks[i]],
                embeddings=[emb.tolist()],
                metadatas=[{
                    "complaint_id": row["Complaint ID"],
                    "product": row["Product"],
                    "company": row["Company"],
                    "issue": row["Issue"],
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }],
                ids=[f"{row['Complaint ID']}_{i}"]
            )

    # PersistentClient automatically persists, no need to call client.persist()
    print("Task 2 completed. Vector store saved in 'vector_store/'.")

if __name__ == "__main__":
    run_task2()
