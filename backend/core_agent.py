#!/usr/bin/env python3

import os
import time
from typing import Annotated, List, Literal, TypedDict, Union, Optional
from functools import lru_cache
import logging

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from llm_utils import get_llm
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
import uuid

# Import performance monitor
from performance_optimizer import perf_monitor, cached_api_call

# Import enhanced components
from enhanced_feature_extractor import EnhancedFeatureExtractor
feature_extractor = EnhancedFeatureExtractor()
print("✅ Using Enhanced Feature Extractor (20 features)")

from langgraph.graph.message import add_messages
from outcome_predictor import OutcomePredictor
from legal_summarizer import LegalSummarizer
from legal_ner import LegalNER


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for features to replace session_state
FEATURE_CACHE = {}

# Store for resolved citations
CITATION_STORE = {}

# Active LLM status tracking
ACTIVE_LLM_PROVIDER = "unknown"
ACTIVE_LLM_MODEL = "unknown"

# Global singletons for heavy models to avoid reloading on every tool call
class ModelCache:
    def __init__(self):
        self.reranker = None
        self.predictor = None
        self.summarizer = None
        self.ner = None

GLOBAL_MODELS = ModelCache()

def get_reranker():
    if not GLOBAL_MODELS.reranker:
        from sentence_transformers import CrossEncoder
        print("🔄 Loading CrossEncoder into memory...")
        GLOBAL_MODELS.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')
    return GLOBAL_MODELS.reranker

def get_predictor():
    if not GLOBAL_MODELS.predictor:
        print("🔄 Loading OutcomePredictor into memory...")
        predictor = OutcomePredictor(model_dir="models")
        predictor.load_model()
        GLOBAL_MODELS.predictor = predictor
    return GLOBAL_MODELS.predictor

def get_summarizer():
    if not GLOBAL_MODELS.summarizer:
        print("🔄 Loading LegalSummarizer into memory...")
        GLOBAL_MODELS.summarizer = LegalSummarizer()
    return GLOBAL_MODELS.summarizer

def get_ner():
    if not GLOBAL_MODELS.ner:
        print("🔄 Loading LegalNER into memory...")
        GLOBAL_MODELS.ner = LegalNER()
    return GLOBAL_MODELS.ner

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    step_count: int

def create_agent(vector_store, bm25_index=None, bm25_corpus=None):
    """
    Creates an optimized LangGraph agent with Hybrid Search (FAISS + BM25).
    """
    
    # 1. Define optimized tools with caching
    @tool
    def search_legal_docs(query: str, jurisdiction: Optional[str] = None):
        """
        Searches the internal legal database using Hybrid Search (Dense + Sparse).
        Provide a 'jurisdiction' like 'Delhi High Court' if the user asks for precedents from a specific court.
        """
        perf_monitor.start_timer()
        print(f"DEBUG: Tool called with query: '{query}', jurisdiction: '{jurisdiction}'")
        
        try:
            if not vector_store:
                return "Error: Vector store not initialized."

            # --- HYBRID SEARCH LOGIC ---
            
            # 1. Dense Search (FAISS or Milvus)
            filter_expr = f"jurisdiction == '{jurisdiction}'" if jurisdiction and jurisdiction != "All" else None
            dense_results = vector_store.similarity_search(query, k=20, filter=filter_expr) # Get top 20
            
            # 2. Sparse Search (BM25)
            sparse_results = []
            if bm25_index and bm25_corpus:
                try:
                    tokenized_query = query.lower().split()
                    # Get top 20 from BM25
                    bm25_top_n = bm25_index.get_top_n(tokenized_query, bm25_corpus, n=20)
                    # Convert strings back to Documents (This assumes bm25_corpus mirrors vector_store content)
                    # Note: Ideally bm25_corpus should be a list of Document objects, but rank_bm25 expects list of tokens.
                    # We need a mapping. If passed purely as text list, we lose metadata.
                    # Simplified strategy: If 'bm25_corpus' is just text, we skip metadata for this part or 
                    # rely on FAISS results primarily if mapping is hard. 
                    # Use 'dense_results' as the source of truth for objects if exact match found?
                    # Better: Assume `bm25_corpus` is a list of Document objects wrapper or we handle it in `api.py`.
                    # For now, let's look at `bm25_index`. If `bm25_corpus` is actually a list of Documents, 
                    # we need to tokenize their page_content for the index but store the Doc. 
                    # Here we assume `bm25_corpus` is the list of Documents.
                    sparse_results = bm25_index.get_top_n(tokenized_query, bm25_corpus, n=20)
                except Exception as e:
                    print(f"⚠️ BM25 Search failed: {e}")
            
            # 3. Reciprocal Rank Fusion (RRF)
            # Combine results
            doc_scores = {}
            k_weight = 60
            
            def add_score(doc, rank):
                # Use content as unique key (collisions possible but rare for long text)
                key = doc.page_content
                if key not in doc_scores:
                    doc_scores[key] = {"doc": doc, "score": 0}
                doc_scores[key]["score"] += 1 / (k_weight + rank)

            for i, doc in enumerate(dense_results):
                add_score(doc, i)
            
            for i, doc in enumerate(sparse_results):
                add_score(doc, i)
            
            # Sort by fused score
            fused_results = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)
            top_candidates = [item["doc"] for item in fused_results[:20]] # Candidate pool for Re-ranking
            
            if not top_candidates:
                top_candidates = dense_results[:20]

            # 4. Cross-Encoder Re-ranking
            final_docs = []
            try:
                reranker = get_reranker()
                
                pairs = [[query, doc.page_content] for doc in top_candidates]
                scores = reranker.predict(pairs)
                
                scored_docs = sorted(zip(top_candidates, scores), key=lambda x: x[1], reverse=True)
                final_docs = [doc for doc, score in scored_docs[:5]] # Final Top 5
                
            except Exception as e:
                print(f"⚠️ Re-ranking failed: {e}")
                final_docs = top_candidates[:5]
            
            # Format results
            results = []
            for doc in final_docs:
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', '?')
                chunk_id = str(uuid.uuid4())
                
                # Store snippet for citation resolution
                CITATION_STORE[chunk_id] = {
                    "source": source,
                    "page": page,
                    "chunk_id": chunk_id,
                    "excerpt": doc.page_content[:120]
                }
                
                content = doc.page_content[:1500] 
                results.append(f"[SOURCE:{chunk_id}]\nContent: {content}...\n")
            
            content = "\n\n".join(results)
            perf_monitor.end_timer("vector_searches")
            perf_monitor.metrics["vector_searches"] += 1
            return content
            
        except Exception as e:
            perf_monitor.end_timer("vector_searches")
            return f"Error searching documents: {str(e)}"

    @tool
    @lru_cache(maxsize=128)
    def search_indian_kanoon(query: str):
        """
        Searches the Indian Kanoon database for legal cases and statutes.
        """
        perf_monitor.start_timer()
        print(f"DEBUG: Indian Kanoon Tool called with query: {query}")
        
        api_token = os.getenv("INDIAN_KANOON_API_TOKEN")
        if not api_token:
            return "Error: Indian Kanoon API token not found."
        
        def make_api_call():
            import requests
            url = "https://api.indiankanoon.org/search/"
            headers = {"Authorization": f"Token {api_token}"}
            params = {"formInput": query, "pagenum": 0}
            
            response = requests.post(url, headers=headers, data=params, timeout=5)
            response.raise_for_status()
            return response.json()
        
        try:
            data = cached_api_call(make_api_call, f"indian_kanoon_{query}")
            
            docs = data.get('docs', [])[:3]
            if not docs:
                perf_monitor.end_timer("api_calls")
                return "No relevant documents found on Indian Kanoon."
            
            results = []
            for doc in docs:
                title = doc.get('title', 'No Title')[:100]
                snippet = doc.get('headline', 'No Snippet')[:200]
                results.append(f"Title: {title}\nSnippet: {snippet}\n")
            
            content = "\n\n".join(results)
            perf_monitor.end_timer("api_calls")
            perf_monitor.metrics["api_calls"] += 1
            return content
            
        except Exception as e:
            perf_monitor.end_timer("api_calls")
            return f"Error searching Indian Kanoon: {str(e)}"

    @tool
    def predict_case_outcome(case_description: str):
        """
        Predicts the outcome of a legal case using Gradient Boosting model.
        """
        perf_monitor.start_timer()
        print(f"DEBUG: Outcome Prediction Tool called with: {case_description}")
        
        try:
            cache_key = f"features_{hash(case_description)}"
            if cache_key in FEATURE_CACHE:
                features = FEATURE_CACHE[cache_key]
            else:
                features = feature_extractor.extract_all_features(case_description)
                FEATURE_CACHE[cache_key] = features
            
            predictor = get_predictor()
            result = predictor.predict(features)
            
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            return result
            
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error predicting outcome: {str(e)}"

    @tool
    def summarize_legal_document(text: str, max_length: int = 200):
        """
        Summarizes legal documents. Use this when the user asks you to summarize an uploaded document or case text.
        """
        perf_monitor.start_timer()
        try:
            summarizer = get_summarizer()
            result = summarizer.summarize(text, max_length=max_length)
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            return result
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error summarizing document: {str(e)}"

    @tool
    def extract_entities(text: str):
        """
        Extracts legal entities from text using Local NLP (Spacy).
        """
        perf_monitor.start_timer()
        try:
            # Use Local NER
            ner = get_ner()
            # Use get_entity_summary for a nice formatted string
            summary = ner.get_entity_summary(text)
            
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            return summary
                
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error extracting entities: {str(e)}"

    # 2. Create tool list
    tools = [search_legal_docs, search_indian_kanoon, predict_case_outcome, summarize_legal_document, extract_entities]
    
    # 3. Lazy LLM initialization
    llm, provider = get_llm()
    ACTIVE_LLM_PROVIDER = provider
    ACTIVE_LLM_MODEL = getattr(llm, "model", getattr(llm, "model_name", "unknown"))
    print(f"✅ LLM initialized: {ACTIVE_LLM_PROVIDER} ({ACTIVE_LLM_MODEL})")

    
    # 4. Create tool node
    tool_node = ToolNode(tools)
    
    # 5. Define optimized agent logic
    def should_continue(state: AgentState) -> Literal["tools", END]:
        messages = state["messages"]
        last_message = messages[-1]
        
        step_count = state.get("step_count", 0)
        if step_count >= 10:
            return END
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    def call_model(state: AgentState):
        messages = state["messages"]
        
        system_prompt = """You are an expert Legal AI Assistant specializing in Indian law. Providing accurate, well-structured legal information.

PERSONA ENFORCEMENT (CRITICAL):
1. NEVER break character. You are the Legal Research Engine.
2. DO NOT act as an AI coding assistant. DO NOT talk about "developing a RAG pipeline", "sample data", or "helping me understand". 
3. If the user pastes a document (like an FIR or patent), immediately act as a lawyer analyzing its legal implications.

RESPONSE GUIDELINES:
1. Provide COMPREHENSIVE and HIGHLY DETAILED professional legal analysis. Do not omit important details. Address the legal query thoroughly with all relevant findings.
2. For case analysis, ALWAYS include a detailed "Winning Prediction" section by using the `predict_case_outcome` tool. Do not guess the outcome without using the ML tool.
3. Cite all relevant laws, statutes, and case precedents that you found.
4. Structure responses with clear headings.
5. Include in-depth, practical legal implications and reasoning.
6. NEVER show debug information or raw tool outputs.
7. Format entity extraction results naturally and shortly.
8. NEVER use placeholders like 'X' or 'Y'.

GROUNDING INSTRUCTIONS (CRITICAL):
1. You strictly answer based on the retrieved context.
2. If the context does not contain the answer, say "I don't know based on the available documents."
3. For every factual claim, you MUST append the source in brackets using the EXACT format: [SOURCE:chunk_id] inline, e.g., "The court stated [SOURCE:123e4567-e89b-12d3...]"
4. Do not cite general knowledge unless explicitly asked for external info.

WINNING PREDICTION REQUIREMENTS:
- Predict probability/winner using the machine learning tool `predict_case_outcome`.
- Provide confidence level (High/Medium/Low) as returned by the tool calculation.
- List key supporting factors.

TOOL USAGE INSTRUCTIONS:
- Whenever the user specifies a particular court (e.g., "[Jurisdiction Context: Delhi High Court]"), you MUST pass `jurisdiction="Delhi High Court"` to `search_legal_docs` tool.
- If the user asks for cases from all courts, do not pass the jurisdiction parameter or pass "All".
- Use summarize_legal_document when the user asks you to summarize an uploaded document or case text.

Use tools wisely."""
        
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm.invoke(messages)
        return {"messages": [response], "step_count": state.get("step_count", 0) + 1}
    
    # 6. Build the graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
