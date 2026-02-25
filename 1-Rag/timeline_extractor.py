"""
Case Chronology Timeline Extractor
Uses LLM (Groq) to extract events and dates from legal text and create a timeline.
"""

import os
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimelineEvent(BaseModel):
    """Schema for a single timeline event"""
    date: str = Field(description="Date in YYYY-MM-DD format, or 'Unknown' if cannot be determined")
    title: str = Field(description="Brief title/name of the event (max 10 words)")
    description: str = Field(description="Detailed description of what happened")
    
class TimelineExtractor:
    """Extract chronological events from legal case text"""
    
    def __init__(self):
        """Initialize the Timeline Extractor with Groq LLM"""
        # Initialize Ollama LLM
        self.llm = ChatOllama(
            model="llama3",
            temperature=0.0
        )
        
        # Parser for structured output
        self.parser = JsonOutputParser(pydantic_object=TimelineEvent)
        
    def extract_date_paragraphs(self, text: str) -> List[str]:
        """
        Pre-filter paragraphs that likely contain dates to reduce token usage.
        Returns list of relevant paragraphs.
        """
        # Common date patterns (including ordinal numbers like 1st, 2nd, 10th, etc.)
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',     # YYYY-MM-DD
            # Ordinal dates: 1st, 2nd, 3rd, 4th, 10th, etc.
            r'\b\d{1,2}(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4}\b',
            r'\b\d{1,2}(?:st|nd|rd|th)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s*,?\s*\d{4}\b',
            # Full month names
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
            # Abbreviated month names
            r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s+\d{4}\b',
            # Generic patterns
            r'\bon\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\bdated?\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\bdate:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        ]
        
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        relevant_paras = []
        for para in paragraphs:
            # Check if paragraph contains any date pattern
            if any(re.search(pattern, para, re.IGNORECASE) for pattern in date_patterns):
                relevant_paras.append(para.strip())
                
        return relevant_paras
    
    def extract_chronology(self, text: str) -> List[Dict]:
        """
        Extract timeline events from legal case text.
        
        Args:
            text: Full legal case text (FIR, Judgment, etc.)
            
        Returns:
            List of timeline events sorted by date
        """
        try:
            # Step 1: Pre-filter to reduce token count
            relevant_paragraphs = self.extract_date_paragraphs(text)
            
            if not relevant_paragraphs:
                logger.warning("No date-containing paragraphs found in text")
                return []
            
            # Join relevant paragraphs (limit to first 15 to avoid token overflow)
            filtered_text = "\n\n".join(relevant_paragraphs[:15])
            
            # Step 2: Use LLM to extract structured events
            system_prompt = """You are a precise legal document analyzer. Your task is to extract chronological events from legal case text.

CRITICAL RULES:
1. Extract ONLY factual events with specific dates or time references
2. Convert all dates to YYYY-MM-DD format when possible
3. If a date is relative (e.g., "next day", "two weeks later"), try to resolve it based on context
4. If absolute date cannot be determined, use "Unknown" for the date field
5. Each event must have: date, title (concise), description (detailed)
6. Return VALID JSON ONLY - no markdown, no code blocks, no comments

{format_instructions}

Extract events from the following legal text:"""

            user_prompt = filtered_text[:4000]  # Limit to ~4000 chars to stay within token limits
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt)
            ])
            
            chain = prompt | self.llm | self.parser
            
            # Invoke the chain
            result = chain.invoke({"format_instructions": self.parser.get_format_instructions()})
            
            # Handle both list and single object responses
            if isinstance(result, list):
                events = result
            elif isinstance(result, dict):
                events = [result]
            else:
                events = []
            
            # Sort by date (put "Unknown" dates at the end)
            def sort_key(event):
                date_str = event.get('date', 'Unknown')
                if date_str == 'Unknown' or not date_str:
                    return '9999-99-99'  # Sort to end
                return date_str
            
            sorted_events = sorted(events, key=sort_key)
            
            logger.info(f"Extracted {len(sorted_events)} timeline events")
            return sorted_events
            
        except Exception as e:
            logger.error(f"Timeline extraction failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


# Test function
def test_timeline_extractor():
    """Test the timeline extractor with sample legal text"""
    
    sample_text = """
    FIR No. 234/2023
    
    On 15th January 2023, the complainant Mr. Rajesh Kumar filed a complaint at the 
    City Police Station alleging theft of his motorcycle (Registration No. DL-8C-1234).
    
    The incident occurred on 14th January 2023 at approximately 3:00 PM when the complainant 
    had parked his vehicle outside the shopping mall.
    
    Police investigation commenced on 16th January 2023. The investigating officer visited 
    the crime scene and recorded statements of witnesses.
    
    On 20th January 2023, CCTV footage was obtained from the mall which showed two suspects.
    
    The accused persons were arrested on 25th January 2023 from their residence in Sector 15.
    
    Charge sheet was filed on 10th February 2023 in the Court of Metropolitan Magistrate.
    """
    
    extractor = TimelineExtractor()
    events = extractor.extract_chronology(sample_text)
    
    print("\n" + "="*60)
    print("EXTRACTED TIMELINE:")
    print("="*60)
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event.get('title')}")
        print(f"   Date: {event.get('date')}")
        print(f"   Description: {event.get('description')}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_timeline_extractor()
