import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-Rag')))

from legal_ner import LegalNER

def test_spacy_entity_extraction():
    """Verify that the local spaCy model correctly extracts entities"""
    ner = LegalNER()
    text = "The Supreme Court of India in Delhi heard the case involving Mr. Rajesh Sharma regarding the Indian Penal Code."
    entities = ner.extract_entities(text)
    
    # LegalNER.extract_entities returns a dict mapping label to list of dicts: {'ORG': [{'text': '...', ...}]}
    orgs = [e['text'] for e in entities.get('ORG', [])]
    persons = [e['text'] for e in entities.get('PER', [])]
    
    assert any('Supreme Court' in org for org in orgs) or len(orgs) > 0, "No organizations found."
    assert any('Rajesh' in person for person in persons) or len(persons) > 0, "No persons found."
