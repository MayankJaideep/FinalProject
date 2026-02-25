from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
import io
from processor import PDFProcessor
from embeddings import MultimodalEmbedder
from vector_db import MilvusHandler
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal Ingestion Service", version="1.0")

# Initialize components
try:
    processor = PDFProcessor()
    embedder = MultimodalEmbedder()
    vector_db = MilvusHandler()
    logger.info("All components initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    # In production, we might want to exit or retry, but for now we log it.

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingests a PDF document:
    1. Extracts text and images (pages).
    2. Generates embeddings for both.
    3. Inserts into Vector DB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    start_time = time.time()
    try:
        content = await file.read()
        logger.info(f"Processing file: {file.filename}")

        # 1. Process PDF
        # Returns list of (page_num, text, image)
        extracted_data = processor.process_pdf(content, file.filename)
        logger.info(f"Extracted {len(extracted_data)} pages/images from {file.filename}")

        entities = []
        
        # Prepare data for insertion
        # Milvus needs columnar data: [ids], [filenames], [page_nums], [texts], [modalities], [vectors]
        # But our insert method expects a list of dictionaries if using high level, 
        # or list of lists for low level.
        # Let's adjust based on MilvusHandler.insert_data which expects:
        # [ [filename...], [page_number...], ... ]
        
        filenames = []
        page_numbers = []
        texts = []
        modalities = []
        vectors = []

        for page_num, text, image in extracted_data:
            # -- Text Modality --
            # Embed text (if sufficient length)
            if len(text.strip()) > 10:
                text_emb = embedder.embed_text(text[:1000]) # Truncate for embedding model limit if needed
                filenames.append(file.filename)
                page_numbers.append(page_num)
                texts.append(text[:60000]) # Limit for DB varchar
                modalities.append("text")
                vectors.append(text_emb.tolist())

            # -- Image Modality --
            # Embed image
            img_emb = embedder.embed_image(image)
            filenames.append(file.filename)
            page_numbers.append(page_num)
            texts.append("[IMAGE]") # Placeholder for text content field for image entries
            modalities.append("image")
            vectors.append(img_emb.tolist())

        if not vectors:
             return JSONResponse(content={"message": "No content extracted to index."}, status_code=200)

        # Insert into Milvus
        data_to_insert = [
            filenames,
            page_numbers,
            texts,
            modalities,
            vectors
        ]
        
        insert_res = vector_db.insert_data(data_to_insert)
        
        duration = time.time() - start_time
        return {
            "message": f"Successfully ingested {file.filename}",
            "pages_processed": len(extracted_data),
            "vectors_inserted": len(vectors),
            "duration_seconds": round(duration, 2)
        }

    except Exception as e:
        logger.error(f"Error ingesting file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
