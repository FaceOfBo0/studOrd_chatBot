import chromadb
from chromadb.api import ClientAPI


def initDB(dbpath: str = "") -> ClientAPI:
    if (dbpath == ""):
        return chromadb.Client()
    return chromadb.PersistentClient(dbpath)