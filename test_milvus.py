import os
from pymilvus import MilvusClient
milvus_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "services", "ingestion", "milvus_demo.db"))
print(f"Loading Milvus from {milvus_db_path}")
client = MilvusClient(uri=milvus_db_path)
print("Loaded Milvus")
