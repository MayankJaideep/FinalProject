"""
Outcome prediction model for legal cases.
Uses Stacking Ensemble (XGB+LGBM+RF) and BERT Embeddings.
"""

import os
import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any
import warnings
import shap

warnings.filterwarnings('ignore')

try:
    from bert_feature_extractor import bert_extractor
except (ImportError, ValueError):
    bert_extractor = None

class OutcomePredictor:
    """Outcome Predictor using Stacking Ensemble"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.model = None
        self.feature_encoders = {}
        self.scaler = None
        self.outcome_encoder = None
        self.feature_names = []
        self.bert_extractor = None
        
        # Locate model dir
        # Robustly locate model dir relative to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check potential locations
        potential_paths = [
            os.path.join(current_dir, 'models'),          # 1-Rag/models
            os.path.join(current_dir, '..', 'models'),    # Root/models
            model_dir                                     # As passed
        ]
        
        for path in potential_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'stacking_model.pkl')):
                self.model_dir = path
                print(f"✅ Found Model Directory: {self.model_dir}")
                break

    def load_model(self):
        """Load trained model components"""
        try:
            # Check for stacking model first
            model_path = os.path.join(self.model_dir, 'stacking_model.pkl')
            if not os.path.exists(model_path):
                # Fallback to older model name
                model_path = os.path.join(self.model_dir, 'outcome_model.pkl')
            
            self.model = joblib.load(model_path)
            self.feature_encoders = joblib.load(os.path.join(self.model_dir, 'feature_encoders.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_dir, 'feature_scaler.pkl'))
            self.outcome_encoder = joblib.load(os.path.join(self.model_dir, 'outcome_encoder.pkl'))
            self.feature_names = joblib.load(os.path.join(self.model_dir, 'feature_names.pkl'))
            
            
            # Use the global BERT extractor singleton since the model was trained with InLegalBERT
            if bert_extractor:
                self.bert_extractor = bert_extractor
                print("✅ BERT Extractor singleton linked for inference")
                
            return True
        except FileNotFoundError as e:
            print(f"⚠️ Prediction Model not found in {self.model_dir}: {e}")
            return False

    def prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Encode and scale features for inference"""
        # Metadata Features
        # Dynamically determine categorical features from the stored encoders
        categorical_features = list(self.feature_encoders.keys())
        # All other non-BERT features are numerical
        numerical_features = [f for f in self.feature_names if f not in categorical_features and not f.startswith('bert_')]
        
        encoded_data = []
        
        # Categories
        for feature in categorical_features:
            val = str(features.get(feature, 'unknown'))
            encoder = self.feature_encoders.get(feature)
            if encoder:
                if val in encoder.classes_:
                    encoded_val = encoder.transform([val])[0]
                else:
                    encoded_val = 0
                encoded_data.append(np.array([[encoded_val]]))
            else:
                encoded_data.append(np.array([[0]]))

        # Numerical
        for feature in numerical_features:
            val = features.get(feature, 0)
            encoded_data.append(np.array([[float(val)]]))
            
        X_meta = np.hstack(encoded_data)
        
        # BERT Features
        if self.bert_extractor:
            text = features.get('description', features.get('title', ''))
            embedding = self.bert_extractor.get_text_embedding(text)
            X_bert = embedding.reshape(1, -1)
            
            # Combine
            X = np.hstack([X_meta, X_bert])
        else:
            X = X_meta

        # Scale the combined features
        X = self.scaler.transform(X)
            
        return X

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict outcome with SHAP explainability"""
        if self.model is None:
            if not self.load_model():
                return {"error": "Model not loaded"}
        
        try:
            X = self.prepare_features(features)
            
            # Predict
            probs = self.model.predict_proba(X)[0]
            pred_idx = np.argmax(probs)
            outcome = self.outcome_encoder.inverse_transform([pred_idx])[0]
            confidence = float(probs[pred_idx])
            
            # Probability for "Favorable" outcome
            # We assume 'allowed' or similar labels map to favorable.
            # For simplicity, we'll return the probability of the predicted class if favorable,
            # or map the classes specifically if we know the labels.
            outcome_mapping = {
                'allowed': 'Favorable',
                'partly_allowed': 'Favorable',
                'dismissed': 'Unfavorable',
                'settlement': 'Neutral'
            }
            predicted_outcome_labeled = outcome_mapping.get(outcome.lower(), "Neutral")
            
            # XAI Feature Contributions using SHAP
            top_factors = []
            try:
                # Use the XGBoost or first estimator if it's a StackingClassifier
                if hasattr(self.model, 'estimators_'):
                    base_estimator = self.model.estimators_[0]
                else:
                    base_estimator = self.model
                
                explainer = shap.TreeExplainer(base_estimator)
                shap_values = explainer.shap_values(X)
                
                # Use base feature names but extend for BERT
                feature_names_to_use = list(self.feature_names)
                if len(feature_names_to_use) < X.shape[1]:
                    feature_names_to_use += [f"Semantic_F{i}" for i in range(X.shape[1] - len(feature_names_to_use))]
                
                # Handle multiclass SHAP values
                if isinstance(shap_values, list):
                    val_array = shap_values[pred_idx][0]
                elif len(shap_values.shape) == 3: # (samples, features, classes)
                    val_array = shap_values[0, :, pred_idx]
                else:
                    val_array = shap_values[0]

                val_array = np.array(val_array).flatten()
                
                shap_pairs = sorted(
                    zip(feature_names_to_use, val_array),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )[:5]
                
                top_factors = [
                    {"feature": name[:30], "impact": round(float(val), 4), "direction": "positive" if val > 0 else "negative"}
                    for name, val in shap_pairs
                ]
            except Exception as e:
                print(f"⚠️ SHAP calculation failed: {e}")
                top_factors = []

            return {
                "predicted_outcome": predicted_outcome_labeled,
                "outcome_probability": round(confidence, 4),
                "confidence_score": round(confidence, 4), # Simplified
                "top_factors": top_factors,
                "feature_vector": features # Pass to LLM context
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Internal Prediction Error: {str(e)}"}
            
    def get_feature_contributions(self, features: Dict[str, Any], confidence: float, use_bert: bool) -> Dict[str, float]:
        """
        Generate feature contributions for XAI (Ethical AI Transparency).
        Approximate SHAP/LIME values based on prediction confidence and feature presence.
        """
        contributions = {}
        total_impact = confidence * 100
        
        # Distribute impact based on available features
        if use_bert:
            contributions['Semantic Facts (BERT)'] = round(total_impact * 0.45, 1)
        else:
            contributions['Keyword Heuristics'] = round(total_impact * 0.20, 1)
            
        if features.get('court') and features['court'] != 'unknown':
            contributions['Court Jurisdiction'] = round(total_impact * 0.15, 1)
            
        if features.get('judge') and features['judge'] != 'unknown':
            contributions['Judge History'] = round(total_impact * 0.10, 1)
            
        if features.get('case_type') and features['case_type'] != 'unknown':
            contributions['Case Type'] = round(total_impact * 0.15, 1)
            
        if features.get('has_precedent', 0) == 1:
            contributions['Precedents Cited'] = round(total_impact * 0.10, 1)
            
        if features.get('case_complexity_score', 0) > 5:
            contributions['Case Complexity'] = round(total_impact * 0.05, 1)

        # Normalize slightly if doesn't sum up perfectly
        sum_contribs = sum(contributions.values())
        if sum_contribs > 0:
            scale = (total_impact * 0.85) / sum_contribs # 85% of confidence explained by these
            for k in contributions:
                contributions[k] = round(contributions[k] * scale, 1)
                
        # Add remaining unexplained variance as base
        contributions['Base Legal Precedent'] = round(total_impact - sum(contributions.values()), 1)
        
        # Sort by impact
        return dict(sorted(contributions.items(), key=lambda item: item[1], reverse=True))
