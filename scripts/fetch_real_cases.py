"""
Fetch real legal cases from Indian Kanoon API and label them using LLM (Gemini/Groq).
Extracts detailed structured data to push accuracy > 90%.
"""

import os
import requests
import pandas as pd
import time
import random
from dotenv import load_dotenv
from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

# --- CONFIGURATION ---
INDIAN_KANOON_API = os.getenv("INDIAN_KANOON_API_TOKEN")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Removed
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Removed

OUTPUT_PATH = "1-Rag/data/real_cases_rich.csv" # New rich dataset

# --- LLM SETUP (Multi-Provider) ---
def get_llm():
    """Get the best available LLM"""
    try:
        from langchain_ollama import ChatOllama
        print("⚡ Using Ollama (Llama-3) for Labeling...")
        return ChatOllama(
            model="llama3",
            temperature=0.0
        )
    except Exception as e:
        print(f"⚠️ Ollama Init Failed: {e}")
        raise e

# --- STRUCTURED EXTRACTION MODEL ---
class DetailedCase(BaseModel):
    outcome: Literal['allowed', 'dismissed', 'partly_allowed', 'settlement', 'unknown'] = Field(description="Final outcome of the case")
    lower_court_decision: Literal['convicted', 'acquitted', 'decreed', 'dismissed', 'unknown'] = Field(description="Decision of the lower court being appealed")
    petitioner_type: Literal['state', 'individual', 'corporate', 'unknown'] = Field(description="Category of the petitioner")
    main_statute: str = Field(description="Main act or section mentioned (e.g. 'IPC 302', 'Contract Act')")
    win_probability_estimate: float = Field(description="Estimated win probability based on text (0.0 to 1.0)")

parser = PydanticOutputParser(pydantic_object=DetailedCase)

# --- CORE LOGIC ---
# --- HEURISTICS ---
def infer_outcome_heuristic(title, text):
    """Refined heuristic for high-precision labeling without API"""
    t = title.lower()
    txt = text.lower()
    
    # Strong Signals in Title
    if 'dismissed' in t or 'dismissal' in t: return 'dismissed'
    if 'allowed' in t or 'acquitted' in t or 'quashed' in t or 'decreed' in t: return 'allowed'
    if 'settled' in t or 'compromised' in t: return 'settlement'
    
    # Strong Signals in Snippet (only if very clear)
    if 'appeal is dismissed' in txt: return 'dismissed'
    if 'appeal is allowed' in txt: return 'allowed'
    
    return None

def process_case_text(llm, title, text):
    """Refined extraction using Pydantic Parser"""
    
    # SYSTEM PROMPT: STRICT JSON
    system_prompt = """
    You are a Legal Data Annotator. Extract structured data from the case snippet.
    
    CRITICAL OUTPUT RULES:
    1. Return VALID JSON ONLY.
    2. DO NOT include comments (//) inside the JSON.
    3. DO NOT include markdown code blocks.
    
    {format_instructions}
    """
    
    user_prompt = f"""
    Case Title: {title}
    Text Snippet: {text[:2000]}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])
    
    chain = prompt | llm | parser
    
    try:
        return chain.invoke({"format_instructions": parser.get_format_instructions()})
    except Exception as e:
        print(f"   ⚠️ Parsing/API Error: {e}")
        return None

def fetch_and_process():
    if not INDIAN_KANOON_API:
        print("❌ Error: INDIAN_KANOON_API_TOKEN not set.")
        return

    try:
        llm = get_llm()
    except ValueError as e:
        print(f"❌ {e}")
        return

    queries = [
        "criminal appeal allowed supreme court",
        "criminal appeal dismissed supreme court", 
        "civil appeal allowed",
        "civil appeal dismissed",
        "writ petition allowed",
        "writ petition dismissed",
        "bail granted", 
        "bail rejected",
        "murder conviction upheld",
        "acquittal confirmed",
        "insurance claim allowed",
        "land acquisition compensation enhanced",
        "cheque dishonour conviction",
        "anticipatory bail granted"
    ]
    
    # Load existing
    all_cases = []
    if os.path.exists(OUTPUT_PATH):
        try:
            all_cases = pd.read_csv(OUTPUT_PATH).to_dict('records')
            print(f"📂 Loaded {len(all_cases)} existing cases.")
        except:
            pass
            
    headers = {"Authorization": f"Token {INDIAN_KANOON_API}"}
    
    print(f"🚀 Starting Deep Data Mining ({len(queries)} queries)...")
    
    for q_idx, query in enumerate(queries):
        print(f"\n🔍 Query [{q_idx+1}/{len(queries)}]: '{query}'")
        
        for page in range(8): # Fetch 8 pages (80 cases) per query
            try:
                url = "https://api.indiankanoon.org/search/"
                params = {"formInput": query, "pagenum": page}
                
                resp = requests.post(url, headers=headers, data=params, timeout=10)
                if resp.status_code != 200:
                    print(f"   ⚠️ API Error: {resp.status_code}")
                    break
                    
                docs = resp.json().get('docs', [])
                if not docs: break
                
                new_batch = []
                print(f"   Processing Page {page} ({len(docs)} docs)...")
                
                for doc in docs:
                    title = doc.get('title', '')
                    # Skip if already exists
                    if any(c['title'] == title for c in all_cases):
                        continue
                        
                    text = doc.get('headline', '') + " " + doc.get('doc', '')
                    
                    # 1. Try HEURISTIC First (Fast & Free)
                    heuristic_outcome = infer_outcome_heuristic(title, text)
                    
                    # 2. WEAK SUPERVISION (Query Inference)
                    # If heuristic is unsure, use the query itself as a noisy label
                    label_source = "Heuristic"
                    if not heuristic_outcome:
                        q_lower = query.lower()
                        if 'allowed' in q_lower or 'granted' in q_lower:
                            heuristic_outcome = 'allowed'
                            label_source = "WeakLabel"
                        elif 'dismissed' in q_lower or 'rejected' in q_lower:
                            heuristic_outcome = 'dismissed'
                            label_source = "WeakLabel"
                        elif 'conviction upheld' in q_lower or 'acquittal confirmed' in q_lower:
                            heuristic_outcome = 'dismissed' # Appeal fails
                            label_source = "WeakLabel"

                    if heuristic_outcome:
                        # Success via Heuristic/Weak Label
                        record = {
                            'title': title,
                            'description': text,
                            'court': doc.get('docsource', 'Unknown'),
                            'outcome': heuristic_outcome,
                            'lower_court_decision': 'unknown',
                            'petitioner_type': 'unknown',
                            'main_statute': 'unknown',
                            'win_prob': 1.0 if heuristic_outcome in ['allowed', 'settled'] else 0.0
                        }
                        new_batch.append(record)
                        print(f"     ✅ [{label_source}] {title[:30]}... -> {heuristic_outcome}")
                        
                    else:
                        # 3. LLM Fallback (Only if truly unknown)
                        # Only use for ambiguous cases to save API Limit
                        try:
                            time.sleep(2) # Rate limit padding
                            data = process_case_text(llm, title, text)
                            if data and data.outcome != 'unknown':
                                record = {
                                    'title': title,
                                    'description': text,
                                    'court': doc.get('docsource', 'Unknown'),
                                    'outcome': data.outcome,
                                    'lower_court_decision': data.lower_court_decision,
                                    'petitioner_type': data.petitioner_type,
                                    'main_statute': data.main_statute,
                                    'win_prob': data.win_probability_estimate
                                }
                                new_batch.append(record)
                                print(f"     ✅ [LLM] {title[:30]}... -> {data.outcome}")
                            else:
                                print(f"     skip (unknown)")
                        except Exception as extraction_err:
                            print(f"     ❌ Extraction failed: {extraction_err}")
                            pass
                
                if new_batch:
                    all_cases.extend(new_batch)
                    pd.DataFrame(all_cases).to_csv(OUTPUT_PATH, index=False)
                    print(f"   💾 Saved {len(all_cases)} total cases.")
                
            except Exception as e:
                print(f"   Critical Error on Page: {e}")
                time.sleep(5)
                
            time.sleep(1)

if __name__ == "__main__":
    fetch_and_process()
