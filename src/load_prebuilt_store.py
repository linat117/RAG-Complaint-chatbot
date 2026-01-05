"""
Helper script to load the pre-built vector store from complaint_embeddings.parquet
Task 3: Optional script to use the full pre-built vector store instead of Task 2's sample
"""
import sys
from pathlib import Path
import pandas as pd
import chromadb
from tqdm import tqdm

# Project path
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))


def load_prebuilt_vector_store(
    parquet_path: str,
    vector_store_path: str = "vector_store",
    collection_name: str = "complaints_full"
):
    """
    Load the pre-built vector store from complaint_embeddings.parquet into ChromaDB.
    
    Args:
        parquet_path: Path to complaint_embeddings.parquet file
        vector_store_path: Path where ChromaDB will be stored
        collection_name: Name for the new collection
    """
    print(f"Loading pre-built embeddings from {parquet_path}...")
    
    # Read parquet file
    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df)} chunks from parquet file")
    print(f"Columns: {df.columns.tolist()}")
    
    # Initialize ChromaDB
    print(f"Initializing ChromaDB at {vector_store_path}...")
    client = chromadb.PersistentClient(path=vector_store_path)
    
    # Create or get collection
    try:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists. Deleting and recreating...")
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Full pre-built complaint embeddings"}
    )
    
    # Prepare data for ChromaDB
    # Expected columns: text, embedding, and metadata fields
    print("Preparing data for ChromaDB...")
    
    # Process in batches for efficiency
    batch_size = 1000
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    for i in tqdm(range(0, len(df), batch_size), desc="Indexing chunks"):
        batch = df.iloc[i:i+batch_size]
        
        # Extract data
        documents = batch['text'].tolist() if 'text' in batch.columns else batch.iloc[:, 0].tolist()
        embeddings = batch['embedding'].tolist() if 'embedding' in batch.columns else None
        
        # Prepare metadata
        metadatas = []
        ids = []
        
        for idx, row in batch.iterrows():
            metadata = {}
            # Add all metadata columns except text and embedding
            for col in batch.columns:
                if col not in ['text', 'embedding']:
                    metadata[col] = str(row[col]) if pd.notna(row[col]) else ""
            
            # Generate ID
            complaint_id = metadata.get('complaint_id', str(idx))
            chunk_idx = metadata.get('chunk_index', 0)
            chunk_id = f"{complaint_id}_{chunk_idx}"
            ids.append(chunk_id)
            metadatas.append(metadata)
        
        # Add to ChromaDB
        if embeddings:
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        else:
            # If no embeddings column, ChromaDB will generate them
            # But this shouldn't happen with pre-built embeddings
            print("Warning: No embeddings found in parquet file!")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    print(f"\n✓ Successfully loaded {len(df)} chunks into collection '{collection_name}'")
    print(f"✓ Collection saved to {vector_store_path}")
    print(f"\nTo use this collection, update your RAG pipeline:")
    print(f"  rag = create_rag_pipeline(collection_name='{collection_name}')")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load pre-built vector store from parquet")
    parser.add_argument(
        "--parquet",
        type=str,
        default="data/raw/complaint_embeddings.parquet",
        help="Path to complaint_embeddings.parquet file"
    )
    parser.add_argument(
        "--vector-store",
        type=str,
        default="vector_store",
        help="Path to ChromaDB vector store directory"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="complaints_full",
        help="Name for the ChromaDB collection"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.parquet).exists():
        print(f"Error: Parquet file not found at {args.parquet}")
        print("Please download complaint_embeddings.parquet from the challenge resources.")
        sys.exit(1)
    
    load_prebuilt_vector_store(
        parquet_path=args.parquet,
        vector_store_path=args.vector_store,
        collection_name=args.collection
    )

