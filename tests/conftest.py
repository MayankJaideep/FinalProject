"""
Shared pytest fixtures for Lumina Copilot test suite.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Ensure the 1-Rag module path is visible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-Rag')))


@pytest.fixture
def sample_case_description():
    """A realistic sample case description for testing."""
    return (
        "The petitioner, a commercial entity incorporated under the Companies Act 2013, "
        "filed for recovery of dues amounting to Rs. 45,00,000 from the respondent under "
        "Section 138 of the Negotiable Instruments Act, 1881 after a cheque was dishonoured. "
        "The matter was heard before the Delhi High Court. The respondent claims the debt was "
        "settled via a separate written agreement dated March 2022. Documentary evidence and "
        "witness testimonies were produced by both parties."
    )


@pytest.fixture
def long_case_description():
    """A case description exceeding 2000 characters for boundary testing."""
    base = (
        "The petitioner filed a writ petition under Article 226 of the Constitution of India "
        "challenging the order passed by the respondent authority. The petitioner is engaged "
        "in manufacturing and export of textiles and has been facing undue harassment from the "
        "tax department despite having furnished all required documentation. "
    )
    return base * 20  # Repeat to ensure it's >2000 chars


@pytest.fixture
def mock_vector_store():
    """A mock vector store with a similarity_search method."""
    store = MagicMock()
    store.similarity_search.return_value = [
        MagicMock(page_content="Sample legal text for testing.", metadata={"source": "test_case.pdf"})
    ]
    store.similarity_search_with_score.return_value = [
        (MagicMock(page_content="Cached result."), 0.1)
    ]
    return store


@pytest.fixture
def mock_bm25_index():
    """A mock BM25 index."""
    bm25 = MagicMock()
    bm25.get_scores.return_value = [0.9, 0.7, 0.5]
    return bm25
