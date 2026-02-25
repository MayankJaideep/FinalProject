"""
Feature extraction module for legal cases.
Extracts structured features from case text using NLP and pattern matching.
"""

import re
import os
from typing import Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class FeatureExtractor:
    """Extract structured features from legal case text"""
    
    # Define known courts
    KNOWN_COURTS = [
        "Supreme Court of India",
        "Delhi High Court",
        "Bombay High Court",
        "Madras High Court",
        "Calcutta High Court",
        "Karnataka High Court",
        "Gujarat High Court",
        "Allahabad High Court",
        "Rajasthan High Court",
        "Madhya Pradesh High Court"
    ]
    
    # Define case types
    CASE_TYPES = [
        "Breach of Contract",
        "Trademark Infringement",
        "Copyright Violation",
        "Patent Dispute",
        "Partnership Dispute",
        "Arbitration Matter",
        "Insolvency Proceedings",
        "Shareholder Dispute",
        "Intellectual Property",
        "Commercial Fraud",
        "Joint Venture Dispute",
        "Licensing Agreement",
        "Supply Chain Dispute",
        "Merger & Acquisition Dispute"
    ]
    
    def __init__(self):
        """Initialize feature extractor with LLM fallback"""
        self.llm = ChatOllama(
            model="llama3",
            temperature=0
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_template(
            """You are a legal document analyzer. Extract the following information from the case text:
            
            Case Text: {text}
            
            Extract and return ONLY the following in this exact format:
            Court: [court name]
            Judge: [judge name or "Unknown"]
            Case Type: [type of case]
            Year: [year filed or "Unknown"]
            Complexity: [1-10 scale]
            
            If information is not available, write "Unknown".
            Be concise and precise."""
        )
    
    def extract_court(self, text: str) -> str:
        """Extract court name from text"""
        text_lower = text.lower()
        
        for court in self.KNOWN_COURTS:
            if court.lower() in text_lower:
                return court
        
        # Pattern matching for common court formats
        court_patterns = [
            r"(Supreme Court of India)",
            r"(Delhi High Court)",
            r"(Bombay High Court)",
            r"([\w\s]+High Court)",
            r"([\w\s]+Court)"
        ]
        
        for pattern in court_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def extract_judge(self, text: str) -> str:
        """Extract judge name from text"""
        # Pattern for "Justice [Name]"
        judge_pattern = r"Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        match = re.search(judge_pattern, text)
        
        if match:
            return f"Justice {match.group(1)}"
        
        # Pattern for "Hon'ble Justice [Name]"
        hon_pattern = r"Hon'ble\s+Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        match = re.search(hon_pattern, text)
        
        if match:
            return f"Justice {match.group(1)}"
        
        return "Unknown"
    
    def extract_case_type(self, text: str) -> str:
        """Extract case type from text"""
        text_lower = text.lower()
        
        # Direct matching
        for case_type in self.CASE_TYPES:
            if case_type.lower() in text_lower:
                return case_type
        
        # Keyword-based inference
        if any(word in text_lower for word in ["contract", "breach", "agreement"]):
            return "Breach of Contract"
        elif any(word in text_lower for word in ["trademark", "brand"]):
            return "Trademark Infringement"
        elif any(word in text_lower for word in ["copyright", "reproduction"]):
            return "Copyright Violation"
        elif any(word in text_lower for word in ["patent", "invention"]):
            return "Patent Dispute"
        elif any(word in text_lower for word in ["arbitration", "arbitral"]):
            return "Arbitration Matter"
        elif any(word in text_lower for word in ["insolvency", "bankruptcy", "ibc"]):
            return "Insolvency Proceedings"
        elif any(word in text_lower for word in ["shareholder", "shares"]):
            return "Shareholder Dispute"
        elif any(word in text_lower for word in ["fraud", "misrepresentation"]):
            return "Commercial Fraud"
        
        return "Unknown"
    
    def extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        # Pattern for years (2000-2024)
        year_pattern = r"\b(20[0-2][0-9])\b"
        matches = re.findall(year_pattern, text)
        
        if matches:
            # Return the most recent year found
            years = [int(y) for y in matches if 2000 <= int(y) <= 2024]
            if years:
                return max(years)
        
        return None
    
    def estimate_complexity(self, text: str) -> int:
        """Estimate case complexity (1-10) based on text characteristics"""
        # Simple heuristic based on text length and legal terminology
        
        complexity_score = 5  # Base score
        
        # Length-based adjustment
        word_count = len(text.split())
        if word_count > 1000:
            complexity_score += 2
        elif word_count > 500:
            complexity_score += 1
        elif word_count < 200:
            complexity_score -= 1
        
        # Legal terminology density
        complex_terms = [
            "precedent", "jurisdiction", "constitutional", "statutory",
            "interpretation", "doctrine", "ratio decidendi", "obiter dicta",
            "ultra vires", "bona fide", "prima facie", "res judicata"
        ]
        
        term_count = sum(1 for term in complex_terms if term.lower() in text.lower())
        complexity_score += min(term_count // 2, 2)
        
        # Clamp between 1 and 10
        return max(1, min(10, complexity_score))
    
    def extract_features_with_llm(self, text: str) -> Dict[str, any]:
        """Use LLM to extract features when pattern matching fails"""
        try:
            prompt = self.extraction_prompt.format(text=text[:2000])  # Limit text length
            response = self.llm.invoke(prompt)
            
            # Parse LLM response
            lines = response.content.strip().split('\n')
            features = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'court':
                        features['court'] = value if value != "Unknown" else None
                    elif key == 'judge':
                        features['judge'] = value if value != "Unknown" else None
                    elif key == 'case type':
                        features['case_type'] = value if value != "Unknown" else None
                    elif key == 'year':
                        try:
                            features['year'] = int(value) if value != "Unknown" else None
                        except:
                            features['year'] = None
                    elif key == 'complexity':
                        try:
                            features['complexity'] = int(value) if value != "Unknown" else 5
                        except:
                            features['complexity'] = 5
            
            return features
        
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            return {}
    
    def extract_features(self, text: str, use_llm_fallback: bool = True) -> Dict[str, any]:
        """
        Extract all features from case text.
        
        Args:
            text: Case description or full text
            use_llm_fallback: Whether to use LLM when pattern matching fails
        
        Returns:
            Dictionary of extracted features
        """
        features = {
            'court': self.extract_court(text),
            'judge': self.extract_judge(text),
            'case_type': self.extract_case_type(text),
            'year': self.extract_year(text),
            'complexity': self.estimate_complexity(text)
        }
        
        # Use LLM fallback for missing features
        if use_llm_fallback and any(v in [None, "Unknown"] for v in features.values()):
            llm_features = self.extract_features_with_llm(text)
            
            # Fill in missing features from LLM
            for key, value in llm_features.items():
                if features.get(key) in [None, "Unknown"] and value not in [None, "Unknown"]:
                    features[key] = value
        
        # Set defaults for still-missing features
        if features['court'] == "Unknown":
            features['court'] = "Delhi High Court"  # Default
        if features['judge'] == "Unknown":
            features['judge'] = "Justice A. Kumar"  # Default
        if features['case_type'] == "Unknown":
            features['case_type'] = "Breach of Contract"  # Default
        if features['year'] is None:
            features['year'] = 2023  # Default to recent year
        
        return features

def test_feature_extraction():
    """Test feature extraction with sample cases"""
    
    extractor = FeatureExtractor()
    
    test_cases = [
        """
        Trademark infringement case filed in Bombay High Court in 2023.
        Justice S. Sharma presiding. The plaintiff alleges unauthorized use
        of their registered trademark by the defendant.
        """,
        """
        Breach of contract dispute in Delhi High Court. Filed in 2022.
        The case involves non-performance of contractual obligations.
        """,
        """
        Patent dispute regarding technology invention filed in Supreme Court
        of India in 2024. Complex matter involving multiple prior art references.
        """
    ]
    
    print("🧪 Testing Feature Extraction\n")
    
    for i, case_text in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Text: {case_text.strip()[:100]}...")
        
        features = extractor.extract_features(case_text, use_llm_fallback=False)
        
        print(f"Extracted Features:")
        for key, value in features.items():
            print(f"  - {key}: {value}")
        print()

if __name__ == "__main__":
    test_feature_extraction()
