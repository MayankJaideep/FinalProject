"""
Named Entity Recognition (NER) for Legal Documents
Extract judges, courts, parties, dates, statutes, and other legal entities from text using Spacy.
"""

import spacy
import re
from typing import List, Dict, Optional
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
SPACY_MODEL_CACHE = None

class LegalNER:
    """
    Extract legal entities from text using Spacy (Local NLP)
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize Spacy NER model
        """
        global SPACY_MODEL_CACHE
        
        if SPACY_MODEL_CACHE:
            self.nlp = SPACY_MODEL_CACHE
            logger.info("✅ Using cached Spacy model.")
        else:
            try:
                logger.info(f"🔄 Loading Spacy model: {model_name}")
                self.nlp = spacy.load(model_name)
                SPACY_MODEL_CACHE = self.nlp
                logger.info("✅ Spacy model loaded successfully.")
            except OSError:
                logger.warning(f"⚠️ Model '{model_name}' not found. Downloading...")
                from spacy.cli import download
                download(model_name)
                self.nlp = spacy.load(model_name)
                SPACY_MODEL_CACHE = self.nlp
                logger.info("✅ Spacy model downloaded and loaded.")
            except Exception as e:
                logger.error(f"❌ Failed to load Spacy model: {e}")
                self.nlp = None

    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract all entities from text using Spacy
        """
        if not self.nlp:
            return {'error': 'NER model not initialized'}
        
        if not text or len(text.strip()) < 5:
            return {'error': 'Text too short'}
        
        try:
            doc = self.nlp(text[:500000]) # Limit to avoid memory issues
            
            grouped = defaultdict(list)
            
            for ent in doc.ents:
                label = ent.label_
                text_val = ent.text.strip()
                
                # Filter noise
                if len(text_val) < 2:
                    continue
                    
                grouped[label].append({
                    'text': text_val,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 1.0 # Spacy doesn't give confidence scores by default
                })
            
            # Map Spacy labels to clearer names if needed
            # PERSON -> PER, ORG -> ORG, GPE -> LOC
            mapped_groups = {}
            for k, v in grouped.items():
                if k == 'PERSON': mapped_groups['PER'] = v
                elif k == 'GPE' or k == 'LOC': 
                    if 'LOC' not in mapped_groups: mapped_groups['LOC'] = []
                    mapped_groups['LOC'].extend(v)
                else:
                    mapped_groups[k] = v
            
            return mapped_groups
            
        except Exception as e:
            return {'error': f'Entity extraction failed: {str(e)}'}

    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal-specific entities using pattern matching + Spacy
        """
        entities = {
            'judges': [],
            'courts': [],
            'parties': [],
            'dates': [],
            'statutes': [],
            'case_numbers': [],
            'citations': []
        }
        
        # 1. Regex Extraction (High Precision)
        
        # Judges
        judge_patterns = [
            r"Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"Hon'ble\s+Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"Chief Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"Mr\.\s+Justice\s+([A-Z][a-z]+)"
        ]
        for p in judge_patterns:
            entities['judges'].extend([f"Justice {m}" if isinstance(m, str) else f"Justice {m[0]}" for m in re.findall(p, text)])

        # Courts
        court_patterns = [
            r"(Supreme Court of India)",
            r"([\w\s]+High Court)",
            r"(District Court of [\w\s]+)",
            r"([\w\s]+District Court)"
        ]
        for p in court_patterns:
            entities['courts'].extend(re.findall(p, text, re.IGNORECASE))

        # Dates
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b"
        ]
        for p in date_patterns:
            entities['dates'].extend(re.findall(p, text, re.IGNORECASE))

        # Statutes
        statute_patterns = [
            r"(Section\s+\d+[A-Z]?\s+of\s+[\w\s]+Act)",
            r"(Article\s+\d+[A-Z]?)",
            r"([\w\s]+Act,?\s+\d{4})"
        ]
        for p in statute_patterns:
            matches = re.findall(p, text)
            # Filter matches that are too long (false positives)
            entities['statutes'].extend([m for m in matches if len(m) < 50])

        # Case Numbers
        case_patterns = [
            r"(Civil Appeal No\.\s*\d+\s+of\s+\d{4})",
            r"(Writ Petition No\.\s*\d+\s+of\s+\d{4})",
            r"(SLP\(C\)\s*No\.\s*\d+\s+of\s+\d{4})",
            r"(Cr\.?\s?A\.?\s?No\.?\s?\d+/\d+)"
        ]
        for p in case_patterns:
            entities['case_numbers'].extend(re.findall(p, text, re.IGNORECASE))

        # Citations
        citation_patterns = [
            r"(AIR\s+\d{4}\s+\w+\s+\d+)",
            r"(\d{4}\s+SCC\s+\d+)",
            r"(\(\d{4}\)\s+\d+\s+SCC\s+\d+)"
        ]
        for p in citation_patterns:
            entities['citations'].extend(re.findall(p, text))

        # 2. Spacy Extraction (Semantic)
        ner_data = self.extract_entities(text)
        
        # Parties: People (PER) + Orgs (ORG) excluding Courts
        if 'PER' in ner_data:
            possible_parties = [item['text'] for item in ner_data['PER']]
            # Filter out Judges if they were already captured by Regex
            entities['parties'].extend(possible_parties)
            
        if 'ORG' in ner_data:
            orgs = [item['text'] for item in ner_data['ORG']]
            # Heuristic: Filter out courts from organizations
            clean_orgs = [o for o in orgs if 'court' not in o.lower() and 'tribunal' not in o.lower()]
            entities['parties'].extend(clean_orgs)

        # Dates from Spacy (DATE)
        if 'DATE' in ner_data:
            spacy_dates = [item['text'] for item in ner_data['DATE']]
            entities['dates'].extend(spacy_dates)

        # Deduplicate and Clean Lists
        for key in entities:
            # Clean keys: remove extra whitespace, punctuation
            cleaned = [str(x).strip().strip('.,') for x in entities[key]]
            # Deduplicate preserving order
            seen = set()
            unique = []
            for item in cleaned:
                if item.lower() not in seen and len(item) > 2:
                    seen.add(item.lower())
                    unique.append(item)
            entities[key] = unique
            
        return entities

    def get_entity_summary(self, text: str) -> str:
        """
        Get a formatted summary of extracted entities
        """
        entities = self.extract_legal_entities(text)
        
        summary_lines = []
        
        icons = {
            'judges': '👨‍⚖️', 'courts': '🏛️', 'parties': '👥',
            'dates': '📅', 'statutes': '📜', 'citations': '📚',
            'case_numbers': '🔢'
        }
        
        for key, icon in icons.items():
            if entities[key]:
                items = entities[key][:3] # Top 3
                summary_lines.append(f"{icon} {key.title()}: {', '.join(items)}")
        
        if not summary_lines:
            return "No specific legal entities identified."
            
        return '\n'.join(summary_lines)

# Test function
def test_ner():
    print("=" * 60)
    print("LEGAL NER TEST (Spacy)")
    print("=" * 60)
    
    ner = LegalNER()
    
    sample_text = """
    In the case of Kesavananda Bharati v. State of Kerala, decided on 24th April 1973,
    the Supreme Court of India established the basic structure doctrine. The bench was
    presided over by Chief Justice S.M. Sikri along with Justice Shelat.
    The case involved interpretation of Article 368 of the Constitution of India.
    Judgment cited (1973) 4 SCC 225.
    """
    
    print("\nText:", sample_text.strip())
    print("\n--- Extracted Entities ---")
    summary = ner.get_entity_summary(sample_text)
    print(summary)
    print("=" * 60)

if __name__ == "__main__":
    test_ner()
