"""
Fetch real legal cases from Indian Kanoon API and label them using LLM (Groq) for high-quality training data.
Saves incrementally to avoid data loss.
"""

import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

API_TOKEN = os.getenv("INDIAN_KANOON_API_TOKEN")
BASE_URL = "https://api.indiankanoon.org"

# Initialize LLM for accurate labeling
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    api_key=os.getenv("GROQ_API_KEY")
)

OUTPUT_PATH = "1-Rag/data/real_cases_fetched.csv"

def save_cases_incrementally(new_cases):
    """Save new cases to CSV incrementally"""
    if not new_cases:
        return

    df_new = pd.DataFrame(new_cases)
    # Filter unknown
    df_new = df_new[df_new['outcome'] != 'unknown']
    
    if df_new.empty:
        return

    if os.path.exists(OUTPUT_PATH):
        try:
            existing_df = pd.read_csv(OUTPUT_PATH)
            # Concat and dedup
            final_df = pd.concat([existing_df, df_new]).drop_duplicates(subset=['title'])
        except:
            final_df = df_new
    else:
        final_df = df_new
        
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"💾 Saved {len(final_df)} cases total (Added batch of {len(df_new)})")

def fetch_cases(query, max_pages=3): # Reduced max_pages for speed
    """Fetch cases for a query"""
    if not API_TOKEN:
        print("❌ Error: INDIAN_KANOON_API_TOKEN not set.")
        return []

    print(f"🔍 Fetching cases for query: '{query}'...")
    cases = []
    
    headers = {"Authorization": f"Token {API_TOKEN}"}
    
    for page in range(max_pages):
        try:
            url = f"{BASE_URL}/search/"
            params = {
                "formInput": query,
                "pagenum": page
            }
            
            resp = requests.post(url, headers=headers, data=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                docs = data.get('docs', [])
                
                if not docs:
                    break
                
                print(f"   Page {page}: Processing {len(docs)} cases with LLM...")
                
                page_cases = []
                for doc in docs:
                    title = doc.get('title', '')
                    snippet = doc.get('headline', '') + " " + doc.get('doc', '')
                    
                    # LLM Labeling
                    outcome = classify_outcome_with_llm(title, snippet)
                    
                    if outcome != 'unknown':
                        case = {
                            'title': title,
                            'description': snippet,
                            'court': doc.get('docsource', 'Unknown Court'),
                            'date': doc.get('publishdate', ''),
                            'outcome': outcome
                        }
                        page_cases.append(case)
                
                cases.extend(page_cases)
                # Save after every page to be safe
                save_cases_incrementally(page_cases)
                
                time.sleep(1) # Rate limit
            else:
                print(f"   Error fetching page {page}: {resp.status_code}")
                
        except Exception as e:
            print(f"   Exception: {e}")
            
    return cases

def classify_outcome_with_llm(title, text):
    """Use LLM to infer outcome from text snippet"""
    try:
        prompt = f"""
        Analyze the following legal case snippet and determine the outcome.
        
        Case Title: {title}
        Snippet: {text[:1000]}
        
        Classify into exactly one of these categories:
        - allowed (if appeal allowed, acquitted, suit decreed, granted)
        - dismissed (if appeal dismissed, convicted, suit dismissed, denied)
        - partly_allowed (if modified, partly allowed)
        - settlement (if compromised, settled)
        - unknown (if unclear)
        
        Return ONLY the category name in lowercase.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        result = response.content.strip().lower()
        
        valid_outcomes = ['allowed', 'dismissed', 'partly_allowed', 'settlement']
        
        # Cleanup
        for valid in valid_outcomes:
            if valid in result:
                return valid
        return 'unknown'
        
    except Exception as e:
        # Fallback to heuristic
        return infer_outcome_heuristic(text)

def infer_outcome_heuristic(text):
    """Fallback heuristic"""
    text = text.lower()
    if 'dismissed' in text or 'reject' in text or 'convicted' in text:
        return 'dismissed'
    elif 'allowed' in text or 'granted' in text or 'acquitted' in text or 'quashed' in text:
        return 'allowed'
    return 'unknown'

def main():
    # Focused queries likely to yield clear outcomes
    queries = [
        "criminal appeal allowed supreme court",
        "criminal appeal dismissed supreme court",
        "civil appeal allowed",
        "civil appeal dismissed",
        "writ petition allowed",
        "writ petition dismissed",
        "bail granted",
        "bail rejected",
        "suit decreed specific performance",
        "suit dismissed recovery of money",
        "divorce granted cruelty",
        "murder conviction upheld",
        "acquittal confirmed murder",
        "consumer complaint allowed compensation"
    ]
    
    # Check current count
    if os.path.exists(OUTPUT_PATH):
        try:
            curr = len(pd.read_csv(OUTPUT_PATH))
            print(f"Starting with {curr} existing cases.")
        except:
            pass

    # Fetch more data
    for q in queries:
        fetch_cases(q, max_pages=2) # 2 pages/query is faster

if __name__ == "__main__":
    main()
