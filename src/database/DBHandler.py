import chromadb
from chromadb.api import ClientAPI


def initDB(dbpath: str = "") -> ClientAPI:
    """Initialize a ChromaDB client instance.
    
    Args:
        dbpath: Optional path to persist the database. If empty, an in-memory client is created.
        
    Returns:
        A ChromaDB client instance, either persistent or in-memory.
    """
    if (dbpath == ""):
        return chromadb.Client()
    return chromadb.PersistentClient(dbpath)