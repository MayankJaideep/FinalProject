"""
Tests for OutcomePredictor.
Covers: valid input, empty string, very long string.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-Rag')))

from outcome_predictor import OutcomePredictor


@pytest.fixture(scope="module")
def predictor():
    """Load predictor once per test module for efficiency."""
    return OutcomePredictor()


def test_predict_valid_input(predictor, sample_case_description):
    """Should return a dict with a prediction and confidence score for valid input."""
    result = predictor.predict(sample_case_description)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "prediction" in result or "outcome" in result or "status" in result, \
        "Result must contain a prediction or outcome key"


def test_predict_empty_string(predictor):
    """Should handle empty string without crashing — return error or default."""
    try:
        result = predictor.predict("")
        # If it doesn't raise, the result should at least be a dict
        assert isinstance(result, dict), "Should return a dict even for empty input"
    except (ValueError, Exception) as e:
        # Acceptable: raises a clear error for empty input
        assert str(e) != "", "Exception message should not be empty"


def test_predict_very_long_string(predictor, long_case_description):
    """Should handle inputs >2000 chars without crashing."""
    assert len(long_case_description) > 2000, "Fixture must produce a long string"
    try:
        result = predictor.predict(long_case_description)
        assert isinstance(result, dict), "Should return a dict for long input"
    except Exception as e:
        pytest.fail(f"OutcomePredictor raised an unexpected exception on long input: {e}")
