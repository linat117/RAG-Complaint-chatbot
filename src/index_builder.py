import chromadb

def create_chroma_client(persist_directory: str = None):
    """
    Create a Chroma client with new API using PersistentClient.
    """
    if persist_directory:
        client = chromadb.PersistentClient(path=persist_directory)
    else:
        client = chromadb.Client()  # In-memory client for non-persistent use
    return client
