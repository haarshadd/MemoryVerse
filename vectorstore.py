"""
Module 5: Smart Retrieval System
Wraps ChromaDB (local, no server needed) with sentence-transformers embeddings
so users can search in natural language ("show my AI projects") instead of
browsing folders. Original files always stay in data/uploads/ untouched.
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

DB_PATH = "data/chroma_db"
COLLECTION_NAME = "documents"

_embedding_fn = embedding_functions.ONNXMiniLM_L6_V2()

_client = chromadb.PersistentClient(
    path=DB_PATH, settings=Settings(anonymized_telemetry=False)
)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=_embedding_fn
)


def add_document(doc_id: str, text: str, metadata: dict):
    """Store a document's text + metadata for later semantic search.
    metadata should include: category, title, date, skills (as comma string),
    file_path — Chroma metadata values must be str/int/float/bool."""
    safe_metadata = {
        "category": metadata.get("category", ""),
        "title": metadata.get("title", ""),
        "date": metadata.get("date") or "",
        "skills": ", ".join(metadata.get("skills", [])),
        "file_path": metadata.get("file_path", ""),
        "summary": metadata.get("summary", ""),
    }
    _collection.upsert(
        ids=[doc_id],
        documents=[text[:8000]],  # cap for embedding efficiency
        metadatas=[safe_metadata],
    )


def search(query: str, n_results: int = 10, category_filter: str = None) -> list[dict]:
    """Natural-language semantic search. Optionally restrict to a category
    (e.g. when the query clearly says 'certificates' or 'projects')."""
    where = {"category": category_filter} if category_filter else None
    results = _collection.query(
        query_texts=[query], n_results=n_results, where=where
    )

    hits = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i in range(len(ids)):
        hits.append({
            "id": ids[i],
            "metadata": metadatas[i],
            "text_preview": documents[i][:200],
            "score": 1 - distances[i],  # convert distance to a similarity-ish score
        })
    return hits


def get_all_documents() -> list[dict]:
    """Fetch everything — used for the timeline and graph views."""
    results = _collection.get()
    docs = []
    for i in range(len(results.get("ids", []))):
        docs.append({
            "id": results["ids"][i],
            "metadata": results["metadatas"][i],
            "text": results["documents"][i],
        })
    return docs


def delete_document(doc_id: str):
    _collection.delete(ids=[doc_id])