import chromadb
from chromadb.utils import embedding_functions
from regulations import REGULATIONS

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_collection():
    client = chromadb.Client()
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    
    collection = client.get_or_create_collection(
        name="regulations",
        embedding_function=ef
    )
    
    if collection.count() == 0:
        documents = [r["content"] for r in REGULATIONS]
        metadatas = [{"name": r["name"], "url": r["url"], "category": r["category"]} for r in REGULATIONS]
        ids = [r["id"] for r in REGULATIONS]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    return collection

def search_regulations(query: str, n_results: int = 3) -> list:
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )
    
    relevant = []
    for i in range(len(results["documents"][0])):
        relevant.append({
            "content": results["documents"][0][i],
            "name": results["metadatas"][0][i]["name"],
            "url": results["metadatas"][0][i]["url"],
            "category": results["metadatas"][0][i]["category"],
        })
    
    return relevant