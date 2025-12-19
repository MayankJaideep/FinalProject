#!/usr/bin/env python3

import os
import time
from typing import Annotated, List, Literal, TypedDict, Union
from functools import lru_cache

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig

# Import performance monitor
from performance_optimizer import perf_monitor, cached_api_call

# Import enhanced components
try:
    from enhanced_feature_extractor import EnhancedFeatureExtractor
    feature_extractor = EnhancedFeatureExtractor()
    print("✅ Using Enhanced Feature Extractor (20 features)")
except ImportError:
    from feature_extractor import FeatureExtractor
    feature_extractor = FeatureExtractor()
    print("⚠️  Using Basic Feature Extractor (6 features)")

from langgraph.graph.message import add_messages
from outcome_predictor import OutcomePredictor
from legal_summarizer import LegalSummarizer
from legal_ner import LegalNER
from historical_analyzer import HistoricalAnalyzer

# Global cache for features to replace session_state
FEATURE_CACHE = {}

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def create_agent(vector_store):
    """
    Creates an optimized LangGraph agent with better performance and accuracy.
    Framework agnostic (works with Streamlit and FastAPI).
    """
    
    # 1. Define optimized tools with caching
    @tool
    def search_legal_docs(query: str):
        """
        Searches the internal legal database for relevant case laws, statutes, and documents.
        """
        perf_monitor.start_timer()
        print(f"DEBUG: Tool called with query: {query}")
        
        try:
            if not vector_store:
                return "Error: Vector store not initialized."

            # Use optimized search with top_k=50 for re-ranking
            initial_docs = vector_store.similarity_search(query, k=50)
            
            if not initial_docs:
                perf_monitor.end_timer("vector_searches")
                return "No relevant documents found in the local database."
            
            # Re-ranking with Cross-Encoder
            top_docs = []
            try:
                from sentence_transformers import CrossEncoder
                # Load re-ranker (cached ideally, but here for safety)
                reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')
                
                # Create pairs [query, doc_text]
                pairs = [[query, doc.page_content] for doc in initial_docs]
                scores = reranker.predict(pairs)
                
                # Combine docs with scores and sort
                scored_docs = sorted(zip(initial_docs, scores), key=lambda x: x[1], reverse=True)
                
                # Take top 5
                top_docs = [doc for doc, score in scored_docs[:5]]
                
            except Exception as e:
                print(f"⚠️ Re-ranking failed, falling back to basic search: {e}")
                top_docs = initial_docs[:5]
            
            # Format results
            results = []
            for doc in top_docs:
                source = doc.metadata.get('source', 'Unknown')
                # Include page number if available
                page = doc.metadata.get('page', '?')
                content = doc.page_content[:1500] # Increase context window
                results.append(f"Source: {source} (Page {page})\nContent: {content}...")
            
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
            # Use cached feature extraction
            cache_key = f"features_{hash(case_description)}"
            if cache_key in FEATURE_CACHE:
                features = FEATURE_CACHE[cache_key]
            else:
                features = feature_extractor.extract_all_features(case_description)
                FEATURE_CACHE[cache_key] = features
            
            # Load and use predictor
            predictor = OutcomePredictor(model_dir="models")
            predictor.load_model()
            
            # Make prediction
            result = predictor.predict(features)
            
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            
            return result
            
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error predicting outcome: {str(e)}"

    @tool
    def summarize_document(text: str):
        """
        Summarizes legal documents.
        """
        perf_monitor.start_timer()
        try:
            summarizer = LegalSummarizer()
            result = summarizer.summarize(text)
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            return result
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error summarizing document: {str(e)}"

    @tool
    def extract_entities(text: str):
        """
        Extracts legal entities from text.
        """
        perf_monitor.start_timer()
        try:
            ner = LegalNER()
            entities = ner.extract_entities(text)
            perf_monitor.end_timer("ml_predictions")
            perf_monitor.metrics["ml_predictions"] += 1
            
            if 'error' in entities:
                return entities['error']
            
            formatted_entities = []
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entity_names = [e['text'] for e in entity_list[:3]]
                    formatted_entities.append(f"{entity_type}: {', '.join(entity_names)}")
            
            if formatted_entities:
                return "Key entities identified: " + "; ".join(formatted_entities)
            else:
                return "No specific legal entities identified."
                
        except Exception as e:
            perf_monitor.end_timer("ml_predictions")
            return f"Error extracting entities: {str(e)}"

    # 2. Create tool list
    tools = [search_legal_docs, search_indian_kanoon, predict_case_outcome, summarize_document, extract_entities]
    
    # 3. Create optimized LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=1024
    )
    
    # 4. Create tool node
    tool_node = ToolNode(tools)
    
    # 5. Define optimized agent logic
    def should_continue(state: AgentState) -> Literal["tools", END]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    def call_model(state: AgentState):
        messages = state["messages"]
        
        system_prompt = """You are an expert Legal AI Assistant specializing in Indian law. Provide accurate, well-structured legal information.

RESPONSE GUIDELINES:
1. Provide clear, professional legal analysis.
2. For case analysis, ALWAYS include a "Winning Prediction" section.
3. Cite relevant laws and case precedents.
4. Structure responses with headings.
5. Include practical legal implications.
6. NEVER show debug information or raw tool outputs.
7. Format entity extraction results naturally.
8. NEVER use placeholders like 'X' or 'Y'.

GROUNDING INSTRUCTIONS (CRITICAL):
1. You strictly answer based on the retrieved context.
2. If the context does not contain the answer, say "I don't know based on the available documents."
3. For every factual claim, you MUST append the source in brackets, e.g., [Source: File.pdf].
4. Do not cite general knowledge unless explicitly asked for external info.

WINNING PREDICTION REQUIREMENTS:
- Predict probability/winner.
- Provide confidence level (High/Medium/Low).
- List key supporting factors.

Use tools wisely."""
        
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm.invoke(messages)
        return {"messages": [response]}
    
    # 6. Build the graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
