"""Load central config from config/config.yaml."""
from pathlib import Path
import yaml

def get_project_root():
    return Path(__file__).resolve().parent.parent

def load_config():
    root = get_project_root()
    config_path = root / "config" / "config.yaml"
    if not config_path.exists():
        return get_default_config()
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_default_config():
    return {
        "paths": {
            "raw_data": "data/raw/complaints.csv",
            "processed_data": "data/processed/filtered_complaints.csv",
            "sample_data": "data/processed/sample_complaints.csv",
            "vector_store": "vector_store",
            "evaluation_output": "output/evaluation_results.md",
        },
        "data": {"seed": 42, "sample_size": 12000, "preprocess_eda_chunks": 3},
        "models": {"embedding": "sentence-transformers/all-MiniLM-L6-v2", "llm": "gpt2"},
        "rag": {"collection_name": "complaints", "top_k": 5},
    }

def resolve_path(key: str, subkey: str):
    """Resolve a path from config; returns absolute path."""
    cfg = load_config()
    p = cfg.get("paths", {}).get(subkey, "")
    root = get_project_root()
    if Path(p).is_absolute():
        return p
    return str(root / p)
