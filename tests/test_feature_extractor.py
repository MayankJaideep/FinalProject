"""
Tests for Feature Extractors.
Verifies enhanced extractor returns 20 features, fallback returns 6.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-Rag')))


def test_enhanced_extractor_returns_20_features(sample_case_description):
    """EnhancedFeatureExtractor should produce exactly 20 features."""
    from enhanced_feature_extractor import EnhancedFeatureExtractor
    extractor = EnhancedFeatureExtractor()
    features = extractor.extract_features(sample_case_description)
    assert hasattr(features, '__len__') or isinstance(features, dict), \
        "Features should be array-like or a dict"
    feature_count = len(features) if not isinstance(features, dict) else len(features.keys())
    assert feature_count == 20, (
        f"Enhanced extractor should return 20 features, got {feature_count}"
    )


def test_fallback_extractor_returns_6_features(sample_case_description):
    """Legacy FeatureExtractor (fallback) should produce exactly 6 features."""
    from feature_extractor import FeatureExtractor
    extractor = FeatureExtractor()
    features = extractor.extract_features(sample_case_description)
    assert hasattr(features, '__len__') or isinstance(features, dict), \
        "Features should be array-like or a dict"
    feature_count = len(features) if not isinstance(features, dict) else len(features.keys())
    assert feature_count == 6, (
        f"Fallback extractor should return 6 features, got {feature_count}"
    )
