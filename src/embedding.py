from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_embedding_model(model_name: str = None):
    if model_name is None:
        try:
            from config.load_config import load_config
            model_name = load_config().get("models", {}).get("embedding", DEFAULT_EMBEDDING_MODEL)
        except Exception:
            model_name = DEFAULT_EMBEDDING_MODEL
    return SentenceTransformer(model_name)
