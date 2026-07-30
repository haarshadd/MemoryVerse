"""
Run this directly to isolate whether the hang is the embedding model
downloading/loading, or something else. Run from the memoryverse folder
with your venv activated:

    python diagnose_search.py
"""
import time

print("Step 1: importing chromadb...")
import chromadb
from chromadb.utils import embedding_functions
print("OK\n")

print("Step 2: creating ONNX embedding function (may download model on first run)...")
start = time.time()
ef = embedding_functions.ONNXMiniLM_L6_V2()
print(f"OK ({time.time() - start:.1f}s)\n")

print("Step 3: embedding a test string...")
start = time.time()
result = ef(["hello world, this is a test"])
print(f"OK ({time.time() - start:.1f}s) — vector length: {len(result[0])}\n")

print("Step 4: connecting to Chroma persistent client...")
client = chromadb.PersistentClient(path="data/chroma_db")
print("OK\n")

print("Step 5: getting/creating collection...")
collection = client.get_or_create_collection(name="documents", embedding_function=ef)
print("OK\n")

print("Step 6: running a query against it...")
start = time.time()
results = collection.query(query_texts=["test query"], n_results=3)
print(f"OK ({time.time() - start:.1f}s)")
print(results)

print("\nAll steps completed — if this hangs, note which step number it stopped at.")