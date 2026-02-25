from pymilvus import MilvusClient, DataType
import os

class MilvusHandler:
    def __init__(self, uri="milvus_demo.db", collection_name="legal_rag_multimodal"):
        # Uses Milvus Lite if uri is a local file path
        # Ensure absolute path for reliability
        if not uri.startswith("http"):
            self.uri = os.path.abspath(uri)
        else:
            self.uri = uri
            
        self.collection_name = collection_name
        self.dim = 512 # CLIP dimension
        
        print(f"Connecting to Milvus using URI: {self.uri}")
        try:
            self.client = MilvusClient(uri=self.uri)
            self._create_collection()
            print("Successfully connected to Milvus and initialized collection.")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise e

    def _create_collection(self):
        if self.client.has_collection(self.collection_name):
            print(f"Collection {self.collection_name} exists.")
            return

        # Define schema explicitly
        schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dim)
        schema.add_field(field_name="filename", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="page_number", datatype=DataType.INT64)
        schema.add_field(field_name="text_content", datatype=DataType.VARCHAR, max_length=60000)
        schema.add_field(field_name="modality", datatype=DataType.VARCHAR, max_length=20)
        
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            metric_type="IP",
            index_type="IVF_FLAT",
            params={"nlist": 1024}
        )
        
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"Created collection {self.collection_name} in {self.uri}")

    def insert_data(self, data):
        """
        Converts columnar data (list of lists) from main.py to list of dicts for MilvusClient.
        Input data structure: [filenames, page_numbers, texts, modalities, vectors]
        """
        try:
            filenames = data[0]
            page_numbers = data[1]
            texts = data[2]
            modalities = data[3]
            vectors = data[4]
            
            rows = []
            for i in range(len(filenames)):
                rows.append({
                    "filename": filenames[i],
                    "page_number": page_numbers[i],
                    "text_content": texts[i],
                    "modality": modalities[i],
                    "vector": vectors[i]
                })
            
            res = self.client.insert(
                collection_name=self.collection_name,
                data=rows
            )
            print(f"Inserted {len(rows)} entities. Response: {res}")
            return res
        except Exception as e:
            print(f"Failed to insert data: {e}")
            raise e
