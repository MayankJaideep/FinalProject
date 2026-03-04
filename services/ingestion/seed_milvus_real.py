import pandas as pd
from pymilvus import MilvusClient
from vector_db import MilvusHandler
from embeddings import MultimodalEmbedder
import sys
import os

csv_path = "/Users/mayankjaideep/Desktop/ai-driven-research-engine-main/1-Rag/data/real_cases_rich.csv"
print(f"Loading real cases from {csv_path}...")
try:
    df = pd.read_csv(csv_path).head(100)
    # Filter out empty descriptions
    df = df.dropna(subset=['description'])
    print(f"Loaded {len(df)} real cases.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    sys.exit(1)

print("Initializing Milvus and dropping old mock collection...")
client = MilvusClient(uri="/Users/mayankjaideep/Desktop/ai-driven-research-engine-main/services/ingestion/milvus_demo.db")
if client.has_collection("legal_rag_multimodal"):
    client.drop_collection("legal_rag_multimodal")
    print("Dropped old collection.")

vector_db = MilvusHandler()
embedder = MultimodalEmbedder()

filenames = []
page_numbers = []
texts = []
modalities = []
vectors = []

# Process in smaller batches if necessary, but 471KB is small enough
for i, row in df.iterrows():
    text = str(row.get('description', ''))
    title = str(row.get('title', f'Case_{i}'))
    if len(text) > 10:
        emb = embedder.embed_text(text[:1000])
        filenames.append(title)
        page_numbers.append(1)
        texts.append(text[:60000])
        modalities.append("text")
        vectors.append(emb.tolist())

if vectors:
    print(f"Inserting {len(vectors)} into Milvus...")
    vector_db.insert_data([filenames, page_numbers, texts, modalities, vectors])
    print("Done!")
else:
    print("No valid data to insert.")
