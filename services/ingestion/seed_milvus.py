import pandas as pd
from vector_db import MilvusHandler
from embeddings import MultimodalEmbedder
import sys

print("Loading real cases...")
try:
    df = pd.read_csv("../data/training_cases.csv").head(20) # Use a small subset for speed
except FileNotFoundError:
    print("training_cases.csv not found. Creating dummy data.")
    df = pd.DataFrame([{
        "title": "Mehta v. Union of India",
        "description": "The court heavily weighed the medical documentation provided by the defense, establishing a strong precedent that age and specific medical conditions override standard PMLA bail restrictions.",
        "outcome": "allowed"
    }, {
        "title": "Suresh Trading vs State of Maharashtra",
        "description": "While the medical grounds were similar, the court dismissed the application due to a lack of corroborating chronologies and the applicant being deemed a severe flight risk.",
        "outcome": "dismissed"
    }])

print("Initializing Milvus and Embedder...")
vector_db = MilvusHandler()
embedder = MultimodalEmbedder()

filenames = []
page_numbers = []
texts = []
modalities = []
vectors = []

for i, row in df.iterrows():
    text = str(row.get('description', ''))
    title = str(row.get('title', f'Case_{i}'))
    if len(text) > 10:
        print(f"Embedding case: {title}")
        emb = embedder.embed_text(text[:1000])
        filenames.append(title)
        page_numbers.append(1)
        texts.append(text[:60000])
        modalities.append("text")
        vectors.append(emb.tolist())

if vectors:
    print("Inserting into Milvus...")
    vector_db.insert_data([filenames, page_numbers, texts, modalities, vectors])
    print("Done!")
else:
    print("No valid data to insert.")
