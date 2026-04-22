"""
Enhanced Feature Extractor with 15+ features for improved accuracy.
This replaces the basic 6-feature extractor with advanced feature engineering.
"""

import re
import os
from typing import Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class EnhancedFeatureExtractor:
    """Extract 15+ features from legal cases for better predictions"""
    
    # Known courts with hierarchy
    COURT_HIERARCHY = {
        "Supreme Court of India": 3,
        "Delhi High Court": 2,
        "Bombay High Court": 2,
        "Madras High Court": 2,
        "Calcutta High Court": 2,
        "Karnataka High Court": 2,
        "Gujarat High Court": 2,
        "Allahabad High Court": 2,
        "Rajasthan High Court": 2,
        "Madhya Pradesh High Court": 2
    }
    
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
    
    LEGAL_TERMS = [
        'precedent', 'jurisdiction', 'constitutional', 'statutory',
        'interpretation', 'doctrine', 'ratio decidendi', 'obiter dicta',
        'ultra vires', 'bona fide', 'prima facie', 'res judicata',
        'plaintiff', 'defendant', 'petitioner', 'respondent',
        'appellant', 'judgment', 'decree', 'injunction'
    ]
    
    def __init__(self):
        """Initialize enhanced feature extractor"""
        self.current_year = datetime.now().year
    
    def extract_all_features(self, text: str) -> Dict[str, any]:
        """
        Extract all 15+ features from case text
        
        Returns:
            Dictionary with enhanced features
        """
        # Basic features
        court = self.extract_court(text)
        judge = self.extract_judge(text)
        case_type = self.extract_case_type(text)
        year = self.extract_year(text)
        complexity = self.estimate_complexity(text)
        
        # Enhanced features
        features = {
            # Basic (6 features)
            'court': court,
            'judge': judge,
            'case_type': case_type,
            'year': year,
            'complexity': complexity,
            'legal_domain': self.get_legal_domain(case_type),
            
            # Temporal (3 features)
            'case_age': self.calculate_case_age(year),
            'is_recent': 1 if year >= 2020 else 0,
            'decade': (year // 10) * 10,
            
            # Court hierarchy (3 features)
            'court_level': self.get_court_level(court),
            'is_supreme_court': 1 if 'Supreme' in court else 0,
            'is_high_court': 1 if 'High' in court else 0,
            
            # Case characteristics (5 features)
            'case_complexity_score': self.calculate_detailed_complexity(text),
            'num_parties': self.count_parties(text),
            'has_precedent': self.check_precedent_citation(text),
            'text_length': len(text),
            'num_legal_terms': self.count_legal_terms(text),
            
            # Legal domain (3 features)
            'is_ip_case': 1 if case_type in ['Trademark Infringement', 'Patent Dispute', 'Copyright Violation', 'Intellectual Property'] else 0,
            'is_contract_case': 1 if 'Contract' in case_type or 'Agreement' in case_type else 0,
            'is_corporate_case': 1 if case_type in ['Shareholder Dispute', 'Merger & Acquisition Dispute', 'Joint Venture Dispute'] else 0,
            
            # New Schema Keys (Defaults)
            'lower_court_decision': 'unknown',
            'petitioner_type': 'unknown',
            'main_statute': 'unknown'
        }
        
        return features
    
    # ========== Basic Extraction Methods ==========
    
    def extract_court(self, text: str) -> str:
        """Extract court name"""
        text_lower = text.lower()
        
        for court in self.COURT_HIERARCHY.keys():
            if court.lower() in text_lower:
                return court
        
        # Pattern matching
        court_patterns = [
            r"(Supreme Court of India)",
            r"([\w\s]+High Court)",
            r"([\w\s]+Court)"
        ]
        
        for pattern in court_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Delhi High Court"  # Default
    
    def extract_judge(self, text: str) -> str:
        """Extract judge name"""
        judge_pattern = r"Justice\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        match = re.search(judge_pattern, text)
        
        if match:
            return f"Justice {match.group(1)}"
        
        return "Justice A. Kumar"  # Default
    
    def extract_case_type(self, text: str) -> str:
        """Extract case type"""
        text_lower = text.lower()
        
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
        
        return "Breach of Contract"  # Default
    
    def extract_year(self, text: str) -> int:
        """Extract year"""
        year_pattern = r"\b(20[0-2][0-9])\b"
        matches = re.findall(year_pattern, text)
        
        if matches:
            years = [int(y) for y in matches if 2000 <= int(y) <= self.current_year]
            if years:
                return max(years)
        
        return 2023  # Default
    
    # ========== Enhanced Feature Methods ==========
    
    def get_legal_domain(self, case_type: str) -> str:
        """Map case type to legal domain"""
        domain_mapping = {
            "Trademark Infringement": "Intellectual Property",
            "Copyright Violation": "Intellectual Property",
            "Patent Dispute": "Intellectual Property",
            "Intellectual Property": "Intellectual Property",
            "Breach of Contract": "Contract Law",
            "Licensing Agreement": "Contract Law",
            "Supply Chain Dispute": "Contract Law",
            "Arbitration Matter": "Arbitration",
            "Shareholder Dispute": "Corporate Law",
            "Merger & Acquisition Dispute": "Corporate Law",
            "Joint Venture Dispute": "Corporate Law",
            "Insolvency Proceedings": "Insolvency",
            "Commercial Fraud": "Criminal Law",
            "Partnership Dispute": "Partnership Law"
        }
        
        return domain_mapping.get(case_type, "Contract Law")
    
    def calculate_case_age(self, year: int) -> int:
        """Calculate how old the case is"""
        return self.current_year - year
    
    def get_court_level(self, court: str) -> int:
        """Get court hierarchy level (1-3)"""
        return self.COURT_HIERARCHY.get(court, 1)
    
    def estimate_complexity(self, text: str) -> int:
        """Basic complexity estimation (1-10)"""
        complexity_score = 5
        
        word_count = len(text.split())
        if word_count > 1000:
            complexity_score += 2
        elif word_count > 500:
            complexity_score += 1
        elif word_count < 200:
            complexity_score -= 1
        
        term_count = sum(1 for term in self.LEGAL_TERMS[:8] if term.lower() in text.lower())
        complexity_score += min(term_count // 2, 2)
        
        return max(1, min(10, complexity_score))
    
    def calculate_detailed_complexity(self, text: str) -> int:
        """Detailed complexity calculation (1-10)"""
        score = 0
        
        # Text length factor
        word_count = len(text.split())
        if word_count > 2000:
            score += 4
        elif word_count > 1000:
            score += 3
        elif word_count > 500:
            score += 2
        else:
            score += 1
        
        # Legal terminology density
        term_count = sum(1 for term in self.LEGAL_TERMS if term.lower() in text.lower())
        score += min(term_count // 3, 3)
        
        # Citation complexity
        if self.check_precedent_citation(text):
            score += 2
        
        # Multiple parties
        if self.count_parties(text) > 2:
            score += 1
        
        return max(1, min(10, score))
    
    def count_parties(self, text: str) -> int:
        """Count number of parties involved"""
        vs_count = text.lower().count(' vs ') + text.lower().count(' v. ') + text.lower().count(' versus ')
        return min(vs_count + 1, 10)
    
    def check_precedent_citation(self, text: str) -> int:
        """Check if case cites precedents"""
        citation_patterns = ['AIR', 'SCC', 'SCR', 'cited', 'relying on', 'referred to']
        return 1 if any(pattern.lower() in text.lower() for pattern in citation_patterns) else 0
    
    def count_legal_terms(self, text: str) -> int:
        """Count legal terminology occurrences"""
        count = sum(text.lower().count(term.lower()) for term in self.LEGAL_TERMS)
        return min(count, 100)

# Test function
def test_enhanced_extractor():
    """Test the enhanced feature extractor"""
    extractor = EnhancedFeatureExtractor()
    
    test_case = """
    Trademark infringement case filed in Bombay High Court in 2023.
    Justice S. Sharma presiding. The plaintiff alleges unauthorized use
    of their registered trademark. The case cites AIR 2020 SC 1234 and
    involves complex issues of brand dilution and market confusion.
    Multiple parties are involved in this dispute.
    """
    
    features = extractor.extract_all_features(test_case)
    
    print("Enhanced Features Extracted:")
    print("=" * 60)
    for key, value in features.items():
        print(f"{key:30s}: {value}")
    print("=" * 60)
    print(f"Total features: {len(features)}")

if __name__ == "__main__":
    test_enhanced_extractor()
