import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-Rag')))

def test_translation_logic():
    from deep_translator import GoogleTranslator
    
    # Hindi to English
    hindi_query = "ब्रीच ऑफ कॉन्ट्रैक्ट क्या है?"
    translated_en = GoogleTranslator(source='auto', target='en').translate(hindi_query)
    
    assert "breach" in translated_en.lower() or "contract" in translated_en.lower()
    
    # English to Hindi
    english_response = "A breach of contract occurs when a party fails to fulfill their obligations."
    translated_hi = GoogleTranslator(source='en', target='hi').translate(english_response)
    
    assert "अनुबंध" in translated_hi or "कॉन्ट्रैक्ट" in translated_hi or "उल्लंघन" in translated_hi
