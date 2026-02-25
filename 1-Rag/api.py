from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
import shutil
import numpy as np
from langchain_community.vectorstores import FAISS
from pymilvus import MilvusClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage
from rank_bm25 import BM25Okapi

# Import core agent
from core_agent import create_agent
from outcome_predictor import OutcomePredictor

app = FastAPI(title="Legal AI Research Engine API", version="2.2")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
class AppState:
    vector_store = None
    embeddings_model = None
    bm25_index = None
    bm25_corpus = None
    semantic_cache = {} # {query_embedding_bytes: response_object}
    cache_keys = [] # List of embeddings (np.array)
    cache_values = [] # List of response objects

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
                model_kwargs={"device": "cpu"}
            )
            print("✅ Embeddings Model Loaded (InLegalBERT)")
        except Exception:
            print("⚠️ InLegalBERT loading failed. Falling back to all-MiniLM-L6-v2.")
            state.embeddings_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
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
                model_kwargs={"device": "cpu"}
             )
             print("✅ Embeddings Model Loaded (CLIP Multilingual)")
             
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
            print("⚠️ Vector Store not found. Upload PDFs to initialize.")
            
    except Exception as e:
        print(f"❌ Error loading resources: {e}")

# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "active", 
        "vector_store": state.vector_store is not None,
        "bm25_index": state.bm25_index is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # --- TRANSLATION (Source to English) ---
        if request.language and request.language != 'en':
            try:
                from deep_translator import GoogleTranslator
                translated = GoogleTranslator(source='auto', target='en').translate(request.message)
                request.message = translated
                print(f"🌐 Translated to English: {request.message}")
            except Exception as e:
                print(f"⚠️ Translation to English failed: {e}")

        # --- JURISDICTION CONTEXT ---
        if request.jurisdiction and request.jurisdiction != "All":
            request.message = f"[Jurisdiction Context: {request.jurisdiction}] {request.message}"
            
        # --- SEMANTIC CACHE LOOKUP ---
        query_vec = np.array(state.embeddings_model.embed_query(request.message))
        
        # Simple linear scan (fast for <1000 items)
        best_sim = -1.0
        best_idx = -1
        
        for i, cached_vec in enumerate(state.cache_keys):
            # Cosine similarity (A . B) / (|A|*|B|)
            # Assuming vectors are not normalized, but HF embeddings usually are? 
            # Safest is manual norm.
            norm_q = np.linalg.norm(query_vec)
            norm_c = np.linalg.norm(cached_vec)
            if norm_q > 0 and norm_c > 0:
                sim = np.dot(query_vec, cached_vec) / (norm_q * norm_c)
                if sim > best_sim:
                    best_sim = sim
                    best_idx = i
        
        if best_sim > 0.90:
            print(f"⚡ Cache Hit (Similarity: {best_sim:.4f})")
            return state.cache_values[best_idx]
            
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
        
        # --- UPDATE CACHE ---
        # Evict if full (FIFO)
        if len(state.cache_keys) > 100:
            state.cache_keys.pop(0)
            state.cache_values.pop(0)
            
        state.cache_keys.append(query_vec)
        # Store a copy of response with cached=True for next time
        cached_response = ChatResponse(response=final_message, sources=sources, cached=True)
        state.cache_values.append(cached_response)
        
        return response_obj
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class SimilarityRequest(BaseModel):
    description: str
    jurisdiction: Optional[str] = "All"

@app.post("/similar_cases")
async def similar_cases_endpoint(request: SimilarityRequest):
    try:
        if not state.vector_store:
            raise HTTPException(status_code=500, detail="Vector store not initialized. Upload documents first.")
            
        # 1. Retrieve top 5 most similar cases
        filter_expr = f"jurisdiction == '{request.jurisdiction}'" if request.jurisdiction and request.jurisdiction != "All" else None
        
        # We need raw similarity search to get the Document objects
        similar_docs = state.vector_store.similarity_search(request.description, k=5, filter=filter_expr)
        
        if not similar_docs:
            return {
                "distribution": "No sufficiently similar cases found in the database.",
                "precedents": []
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
            
        # 3. Use LLM to analyze the outcomes of these specific cases
        from langchain_ollama import ChatOllama
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatOllama(model="llama3", temperature=0.1)
        
        analysis_prompt = f"""You are a legal expert analyzing historical precedents. 
Given the user's case description and {len(similar_docs)} similar historical cases retrieved from the database, provide two things:

1. OVERALL DISTRIBUTION: A 2-sentence summary of how these types of cases generally conclude based ONLY on the provided precedents (e.g. "Most similar cases resulted in dismissal due to lack of evidence. However, one case awarded damages.").
2. PRECEDENT OUTCOMES: For each of the {len(similar_docs)} cases, write exactly ONE sentence explaining what happened in that specific case.

User's Case: {request.description}

--- RETRIEVED PRECEDENTS ---
{"".join(context_blocks)}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
OVERALL DISTRIBUTION: [Your 2 sentence summary]
CASE 1 OUTCOME: [1 sentence]
CASE 2 OUTCOME: [1 sentence]
...etc
"""
        messages = [HumanMessage(content=analysis_prompt)]
        response = llm.invoke(messages)
        
        # Parse the LLM response to send cleanly to frontend
        response_text = response.content
        
        distribution = "Analysis unavailable."
        
        if "OVERALL DISTRIBUTION:" in response_text:
            parts = response_text.split("CASE 1 OUTCOME:")
            distribution = parts[0].replace("OVERALL DISTRIBUTION:", "").strip()
            
            # Try to attach the 1-sentence outcomes to the precedent objects
            if len(parts) > 1:
                outcomes_text = "CASE 1 OUTCOME:" + parts[1]
                for i in range(len(precedents)):
                    outcome_marker = f"CASE {i+1} OUTCOME:"
                    next_marker = f"CASE {i+2} OUTCOME:"
                    
                    if outcome_marker in outcomes_text:
                        start_idx = outcomes_text.find(outcome_marker) + len(outcome_marker)
                        end_idx = outcomes_text.find(next_marker) if next_marker in outcomes_text else len(outcomes_text)
                        
                        precedents[i]["outcome_summary"] = outcomes_text[start_idx:end_idx].strip()
                    else:
                        precedents[i]["outcome_summary"] = "Outcome unclear from text."
        else:
             distribution = response_text # Fallback
             for p in precedents:
                 p["outcome_summary"] = "See detailed snippet."
        
        return {
            "distribution": distribution,
            "precedents": precedents
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        documents = []
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
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
        timeline_events = extractor.extract_chronology(case_text)
        
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
