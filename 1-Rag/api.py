from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

# --- MAC OS MULTIPROCESSING FIX ---
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

import uvicorn
import shutil
import numpy as np
import time
import uuid
import json
import logging
from collections import defaultdict
import platform

# Identify if Mac ARM for hardware acceleration
mac_device = "mps" if platform.system() == "Darwin" and platform.machine() == "arm64" else "cpu"

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
from pymilvus import MilvusClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage
from rank_bm25 import BM25Okapi
from fastapi.concurrency import run_in_threadpool

# Import core agent
from core_agent import create_agent
from outcome_predictor import OutcomePredictor

# --- 1. GOVERNANCE & LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [LuminaAPI] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("lumina_api")

app = FastAPI(title="Legal AI Research Engine API", version="2.3")

# --- 2. SECURITY (CORS) ---
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. SECURITY (API KEY AUTH) ---
API_KEY = os.environ.get("LUMINA_API_KEY", "secret-lumina-key-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key and api_key != API_KEY:
        logger.warning("Attempted access with invalid API key.")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    elif not api_key:
        logger.warning("Access without API key. Allowing for backwards compatibility in dev.")
    return api_key or "anonymous"

# --- 4. SECURITY (RATE LIMITING) ---
class SimpleRateLimiter:
    def __init__(self, limit=20, window=60):
        self.requests = defaultdict(list)
        self.limit = limit
        self.window = window

    def __call__(self, request: Request, api_key: str = Depends(verify_api_key)):
        now = time.time()
        client_id = api_key if api_key != "anonymous" else request.client.host
        self.requests[client_id] = [req for req in self.requests[client_id] if now - req < self.window]
        if len(self.requests[client_id]) >= self.limit:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        self.requests[client_id].append(now)
        return client_id

# Global State
class AppState:
    vector_store = None
    embeddings_model = None
    bm25_index = None
    bm25_corpus = None
    semantic_cache_store = None # FAISS-backed semantic cache

state = AppState()

# Models
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    language: str = "en"
    jurisdiction: str = "All"

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, str]] = []
    cached: bool = False

class PredictionRequest(BaseModel):
    description: str
    court: Optional[str] = None
    judge: Optional[str] = None
    case_type: Optional[str] = None
    model_version: str = "advanced"

class PredictionResponse(BaseModel):
    result: Dict[str, Any]

class MilvusLiteWrapper:
    """Wrapper for MilvusClient to mimic LangChain VectorStore interface for similarity_search"""
    def __init__(self, uri, collection_name, embedding_func):
        self.client = MilvusClient(uri=uri)
        self.collection_name = collection_name
        self.embedding_func = embedding_func

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Any]:
        # Generate embedding
        query_vec = self.embedding_func.embed_query(query)
        
        filter_expr = kwargs.get('filter')
        
        # Search
        res = self.client.search(
            collection_name=self.collection_name,
            data=[query_vec],
            limit=k,
            filter=filter_expr,
            output_fields=["text_content", "filename", "page_number", "modality", "jurisdiction"]
        )
        
        documents = []
        if not res:
            return documents
            
        for hit in res[0]:
            entity = hit['entity']
            # Milvus Lite returns entity in 'entity' key usually, or at top level depending on version?
            # MilvusClient search result is list of list of dicts.
            # Dict keys: id, distance, entity={...}
            
            content = entity.get('text_content', '')
            meta = {
                "source": entity.get('filename'),
                "page": entity.get('page_number'),
                "modality": entity.get('modality'),
                "score": hit.get('distance')
            }
            documents.append(Document(page_content=content, metadata=meta))
            
        return documents

    @property
    def docstore(self):
        # Mocking docstore for BM25 (simplified)
        # We can't easily fetch all docs from Milvus without iterator. 
        # Returning empty to skip BM25 for now or implement scroll if needed.
        class MockDocstore:
            _dict = {}
        return MockDocstore()

def update_bm25_index():
    """Helper to rebuild BM25 index from Vector Store documents"""
    if state.vector_store and hasattr(state.vector_store, 'docstore'):
        try:
            print("🔄 Building BM25 Index...")
            # Extract all docs
            docs = list(state.vector_store.docstore._dict.values())
            if not docs:
                return
            
            # Tokenize
            tokenized_corpus = [doc.page_content.lower().split() for doc in docs]
            
            # Build Index
            state.bm25_index = BM25Okapi(tokenized_corpus)
            state.bm25_corpus = docs # Store actual doc objects for retrieval
            print(f"✅ BM25 Index Built ({len(docs)} documents)")
        except Exception as e:
            print(f"⚠️ Failed to build BM25 Index: {e}")

# Startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Legal AI Engine...")
    try:
        # Load Embeddings
        try:
            # Check if InLegalBERT feature extractor initialized it
            # We use langchain wrapper here for vector store compatibility
            state.embeddings_model = HuggingFaceEmbeddings(
                model_name="law-ai/InLegalBERT", # Match the extractor
                model_kwargs={"device": mac_device}
            )
            print(f"✅ Embeddings Model Loaded (InLegalBERT on {mac_device})")
        except Exception:
            print("⚠️ InLegalBERT loading failed. Falling back to all-MiniLM-L6-v2.")
            state.embeddings_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": mac_device}
            )
        
        # Load Vector Store
        # Since running from 1-Rag/, we need to go up one level
        milvus_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "ingestion", "milvus_demo.db"))
        print(f"DEBUG: Checking for Milvus DB at {milvus_db_path}")
        if os.path.exists(milvus_db_path):
             print(f"✅ Found Milvus DB at {milvus_db_path}")
             # Use the same embedding model as ingestion
             state.embeddings_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/clip-ViT-B-32-multilingual-v1",
                model_kwargs={"device": mac_device}
             )
             print(f"✅ Embeddings Model Loaded (CLIP Multilingual on {mac_device})")
             
             try:
                 state.vector_store = MilvusLiteWrapper(
                    uri=milvus_db_path,
                    collection_name="legal_rag_multimodal",
                    embedding_func=state.embeddings_model
                 )
                 print("✅ Milvus Vector Store Loaded (Custom Wrapper)")
             except Exception as e:
                 print(f"❌ Failed to load Milvus Wrapper: {e}")
             
        elif os.path.exists("faiss_store"):
            # Fallback to legacy FAISS
            # Load default embeddings for FAISS if not CLIP
             state.embeddings_model = HuggingFaceEmbeddings(
                model_name="law-ai/InLegalBERT", 
                model_kwargs={"device": "cpu"}
            )
             state.vector_store = FAISS.load_local(
                "faiss_store", state.embeddings_model, allow_dangerous_deserialization=True
            )
             print("✅ Vector Store Loaded (FAISS)")
            
            # Build BM25
             update_bm25_index()
            
        else:
            logger.warning("Vector Store not found. Upload PDFs to initialize.")
            
        # --- SEMANTIC CACHE INIT ---
        cache_path = "semantic_cache_index"
        if os.path.exists(cache_path):
            state.semantic_cache_store = FAISS.load_local(
                cache_path, state.embeddings_model, allow_dangerous_deserialization=True
            )
            logger.info(f"✅ Loaded FAISS Semantic Cache from {cache_path}")
        else:
            # Initialize empty FAISS
            empty_doc = Document(page_content="[cache_init]", metadata={"response": "{}"})
            state.semantic_cache_store = FAISS.from_documents([empty_doc], state.embeddings_model)
            logger.info("✅ Initialized new FAISS Semantic Cache")
            
    except Exception as e:
        logger.error(f"Error loading resources: {e}")

# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "active", 
        "vector_store": state.vector_store is not None,
        "bm25_index": state.bm25_index is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, client_id: str = Depends(SimpleRateLimiter(limit=30, window=60))):
    try:
        # --- TRANSLATION (Source to English) ---
        if request.language and request.language != 'en':
            try:
                from deep_translator import GoogleTranslator
                translated = GoogleTranslator(source='auto', target='en').translate(request.message)
                request.message = translated
                logger.info(f"Translated to English: {request.message}")
            except Exception as e:
                logger.warning(f"Translation to English failed: {e}")

        # --- JURISDICTION CONTEXT ---
        if request.jurisdiction and request.jurisdiction != "All":
            request.message = f"[Jurisdiction Context: {request.jurisdiction}] {request.message}"
            
        # --- SEMANTIC CACHE LOOKUP (FAISS) ---
        if state.semantic_cache_store:
            # We use a tight L2 threshold for "very similar" matches against the persistent FAISS index
            results = state.semantic_cache_store.similarity_search_with_score(request.message, k=1)
            if results:
                doc, l2_distance = results[0]
                if doc.page_content != "[cache_init]" and l2_distance < 0.25:
                    logger.info(f"⚡ Cache Hit (L2 Distance: {l2_distance:.4f})")
                    try:
                        cached_data = json.loads(doc.metadata["response"])
                        return ChatResponse(
                            response=cached_data["response"], 
                            sources=cached_data.get("sources", []), 
                            cached=True
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse cached response: {e}")
        # --- END CACHE ---

        # Initialize Agent
        agent_executor = create_agent(
            state.vector_store,
            bm25_index=state.bm25_index,
            bm25_corpus=state.bm25_corpus
        )
        
        # Convert history
        langchain_history = []
        for msg in request.history[-4:]:  # Limit to last 4 to avoid translation latency
            content = msg['content']
            if request.language and request.language != 'en':
                try:
                    from deep_translator import GoogleTranslator
                    content = GoogleTranslator(source='auto', target='en').translate(content)
                except Exception as e:
                    print(f"⚠️ History translation failed: {e}")
            
            if msg['role'] == 'user':
                langchain_history.append(HumanMessage(content=content))
            elif msg['role'] == 'assistant':
                langchain_history.append(AIMessage(content=content))
        
        langchain_history.append(HumanMessage(content=request.message))
        
        initial_state = {"messages": langchain_history}
        final_state = agent_executor.invoke(initial_state)
        
        final_message = final_state["messages"][-1].content
        
        # --- TRANSLATION (English to Target) ---
        if request.language and request.language != 'en':
            try:
                from deep_translator import GoogleTranslator
                # deep-translator handles limits up to 5000 chars natively for Google Translate
                final_message = GoogleTranslator(source='en', target=request.language).translate(final_message)
                print(f"🌐 Translated response back to target language")
            except Exception as e:
                print(f"⚠️ Translation to {request.language} failed: {e}")
        
        sources = []
        for msg in final_state["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    sources.append({
                        "type": tool_call['name'],
                        "args": str(tool_call['args'])
                    })
        
        response_obj = ChatResponse(response=final_message, sources=sources, cached=False)
        
        # --- UPDATE CACHE (FAISS) ---
        if state.semantic_cache_store:
            cache_meta = {
                "response": json.dumps({
                    "response": final_message,
                    "sources": sources
                })
            }
            cache_doc = Document(page_content=request.message, metadata=cache_meta)
            state.semantic_cache_store.add_documents([cache_doc])
            
            try:
                state.semantic_cache_store.save_local("semantic_cache_index")
            except Exception as e:
                logger.error(f"Failed to save semantic cache: {e}")
        
        return response_obj
        
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

class SimilarityRequest(BaseModel):
    description: str
    jurisdiction: Optional[str] = "All"

@app.post("/similar_cases")
async def similar_cases_endpoint(request: SimilarityRequest, client_id: str = Depends(SimpleRateLimiter(limit=30, window=60))):
    try:
        if not state.vector_store:
            raise HTTPException(status_code=500, detail="Vector store not initialized. Upload documents first.")
            
        # We need raw similarity search to get the Document objects.
        # Handle the syntactic difference between Langchain Milvus (expr="string") and FAISS (filter={"dict"})
        is_faiss = hasattr(state.vector_store, 'index') or state.vector_store.__class__.__name__ == 'FAISS'
        
        if request.jurisdiction and request.jurisdiction != "All":
            if is_faiss:
                similar_docs = state.vector_store.similarity_search(request.description, k=5, filter={"jurisdiction": request.jurisdiction})
            else:
                similar_docs = state.vector_store.similarity_search(request.description, k=5, expr=f"jurisdiction == '{request.jurisdiction}'")
        else:
            similar_docs = state.vector_store.similarity_search(request.description, k=5)
        
        if not similar_docs:
            return {
                "analytics": {
                    "winRate": 0,
                    "avgDuration": "N/A",
                    "judgeTendency": "Unknown",
                    "outcomes": [
                        {"name": "Allowance", "value": 0, "color": "#4F46E5"},
                        {"name": "Dismissal", "value": 0, "color": "#E11D48"},
                        {"name": "Settlement", "value": 0, "color": "#94A3B8"}
                    ]
                },
                "cases": []
            }
            
        # 2. Extract snippets and metadata for the frontend
        precedents = []
        context_blocks = []
        for i, doc in enumerate(similar_docs):
            source = doc.metadata.get('source', 'Unknown Document')
            page = doc.metadata.get('page', '?')
            snippet = doc.page_content[:800] # Limit size
            
            precedents.append({
                "id": i + 1,
                "source": source,
                "page": page,
                "snippet": snippet
            })
            
            context_blocks.append(f"CASE {i+1} [{source}]:\n{snippet}\n")
            
        # 3. Use ChatGroq to analyze the outcomes of these specific cases and generate structured UI data
        # 3. Use ChatGroq to analyze the outcomes of these specific cases and generate structured UI data
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        from typing import List
        import os
        
        class PrecedentCase(BaseModel):
            id: int
            name: str
            year: int
            court: str
            match: int
            outcome: str
            duration_months: int
            factSimilarity: str
            legalSimilarity: str
            tags: List[str]
            reason: str
            
        class CasesList(BaseModel):
            cases: List[PrecedentCase]

        parser = JsonOutputParser(pydantic_object=CasesList)

        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
        
        analysis_prompt = """You are a legal expert analyzing historical precedents for a Prediction Dashboard.
Given the user's case description and {num_cases} similar historical cases retrieved from our database, generate a structured JSON object containing a list of 'cases'.

Extract and synthesize ONLY the 'cases' array for the specific {num_cases} precedents provided below.
- id: integer starting from 1
- name: deduce a case name from the snippet (e.g. "State v. Sharma")
- year: integer (guess based on context or use recent year)
- court: court name
- match: semantic match percentage (0-100)
- outcome: EXACTLY ONE OF "Allowance", "Dismissal", or "Settlement"
- duration_months: integer, estimate resolution time in months based on dates in context, or 0 if unknown
- factSimilarity: "High", "Medium", or "Low"
- legalSimilarity: "High", "Medium", or "Low"
- tags: Array of 2-3 legal tags (e.g. ["Bail", "PMLA"])
- reason: 1-2 sentences explaining the court's reasoning and ratio decidendi based on the snippet.

User's Case: {user_desc}

--- RETRIEVED PRECEDENTS ---
{context}

CRITICAL: Return ONLY valid JSON format matching the schema rules.
{format_instructions}
"""
        prompt = ChatPromptTemplate.from_template(analysis_prompt)
        chain = prompt | llm | parser
        
        try:
            output_json = chain.invoke({
                "num_cases": len(similar_docs),
                "user_desc": request.description,
                "context": "".join(context_blocks),
                "format_instructions": parser.get_format_instructions()
            })
            
            if isinstance(output_json, dict):
                cases_list = output_json.get("cases", [])
            elif isinstance(output_json, list):
                cases_list = output_json
            else:
                cases_list = []
                
            total_cases = len(cases_list)
            
            allowance_count = 0
            dismissal_count = 0
            settlement_count = 0
            total_duration = 0
            cases_with_duration = 0
            
            for c in cases_list:
                outcome = c.get("outcome", "Dismissal")
                if "allowance" in outcome.lower(): 
                    allowance_count += 1
                    c["outcome"] = "Allowance"
                elif "dismissal" in outcome.lower(): 
                    dismissal_count += 1
                    c["outcome"] = "Dismissal"
                else: 
                    settlement_count += 1
                    c["outcome"] = "Settlement"
                
                duration = c.get("duration_months", 0)
                if isinstance(duration, int) and duration > 0:
                    total_duration += duration
                    cases_with_duration += 1
            
            if total_cases > 0:
                win_rate = round((allowance_count / total_cases) * 100)
                dismissal_pct = round((dismissal_count / total_cases) * 100)
                settlement_pct = 100 - win_rate - dismissal_pct
            else:
                win_rate = 0
                dismissal_pct = 0
                settlement_pct = 0
            
            avg_duration_str = f"{int(total_duration / cases_with_duration)} months" if cases_with_duration > 0 else "14 months"
            judge_tendency = "Pro-Allowance" if allowance_count >= dismissal_count else "Strict"
            
            result_json = {
                "analytics": {
                    "winRate": win_rate,
                    "avgDuration": avg_duration_str,
                    "judgeTendency": judge_tendency,
                    "outcomes": [
                        {"name": "Allowance", "value": win_rate, "color": "#4F46E5"},
                        {"name": "Dismissal", "value": dismissal_pct, "color": "#E11D48"},
                        {"name": "Settlement", "value": settlement_pct, "color": "#94A3B8"}
                    ]
                },
                "cases": cases_list
            }
            return result_json
        except Exception as e:
            logger.error(f"Failed to parse Groq response: {e}")
            raise HTTPException(status_code=500, detail="Failed to synthesize precedent analytics.")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(files: List[UploadFile] = File(...), client_id: str = Depends(SimpleRateLimiter(limit=30, window=60))):
    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        documents = []
        MAX_FILE_SIZE = 20 * 1024 * 1024 # 20 MB
        
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid PDF. Only application/pdf files are permitted.")
                
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail=f"File size exceeds 20MB limit.")
                
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(content)
            
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(documents)
        
        if state.vector_store:
            state.vector_store.add_documents(final_documents)
        else:
            state.vector_store = FAISS.from_documents(final_documents, state.embeddings_model)
            
        state.vector_store.save_local("faiss_store")
        
        # Rebuild BM25 after upload
        update_bm25_index()
        
        shutil.rmtree(temp_dir)
        
        return {"message": f"Processed {len(files)} files successfully.", "chunks": len(final_documents)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize/timeline")
async def visualize_timeline(request: dict):
    """
    Extract chronological timeline from legal case text.
    
    Input: {"text": "..."}
    Output: {"events": [...], "message": "..."}
    """
    try:
        case_text = request.get("text", "")
        
        if not case_text or len(case_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Please provide sufficient case text (minimum 50 characters)")
        
        from timeline_extractor import TimelineExtractor
        
        extractor = TimelineExtractor()
        # Use run_in_threadpool to prevent the synchronous LangChain/Ollama call from blocking the FastAPI event loop
        timeline_events = await run_in_threadpool(extractor.extract_chronology, case_text)
        
        if not timeline_events:
            return {
                "events": [],
                "message": "No dated events found in the provided text. Please ensure the text contains specific dates or time references."
            }
        
        return {
            "events": timeline_events,
            "message": f"Successfully extracted {len(timeline_events)} timeline events"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Timeline extraction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
