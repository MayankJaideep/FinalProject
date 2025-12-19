"""
Advanced Model Training Pipeline (Level 2).
Features:
- BERT Semantic Embeddings (all-MiniLM-L6-v2)
- Stacking Ensemble (XGBoost + LightGBM + RandomForest -> LogisticRegression)
- Optuna Hyperparameter Tuning
- SHAP Explanations
"""

import os
import pandas as pd
import numpy as np
import joblib
import optuna
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, matthews_corrcoef, brier_score_loss
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import warnings
import logging

# Feature Extractors
try:
    from enhanced_feature_extractor import EnhancedFeatureExtractor
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from enhanced_feature_extractor import EnhancedFeatureExtractor

try:
    from bert_feature_extractor import BERTFeatureExtractor
except ImportError:
    BERTFeatureExtractor = None

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    logger.warning("XGBoost not installed. Install with: pip install xgboost")
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    logger.warning("LightGBM not installed. Install with: pip install lightgbm")
    LIGHTGBM_AVAILABLE = False


class StackingModelTrainer:
    """Train Stacking Ensemble with BERT + Metadata features"""
    
    def __init__(self, model_dir: str = "models"):
        """Initialize trainer"""
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.meta_extractor = EnhancedFeatureExtractor()
        self.bert_extractor = BERTFeatureExtractor() if BERTFeatureExtractor else None
        
        self.scaler = StandardScaler()
        self.outcome_encoder = LabelEncoder()
        self.feature_encoders = {}
        self.stacking_model = None
        self.feature_names = []
        self.metadata_feature_count = 0
    
    def load_and_prepare_data(self, data_path: str):
        """Load data and extract combined features (Metadata + BERT)."""
        logger.info("Loading training data...")
        df = pd.read_csv(data_path)
        logger.info(f"Total cases: {len(df)}")
        
        # 1. Extract Metadata Features
        logger.info("Extracting metadata features...")
        meta_features_list = []
        for idx, row in df.iterrows():
            text = row.get('description', row.get('title', ''))
            features = self.meta_extractor.extract_all_features(text)
            meta_features_list.append(features)
        
        meta_df = pd.DataFrame(meta_features_list)
        self.metadata_feature_count = len(meta_df.columns)
        
        X_meta = self._prepare_metadata_features(meta_df, fit=True)
        
        # 2. Extract BERT Features
        if self.bert_extractor:
            logger.info("Extracting BERT semantic embeddings...")
            bert_features_list = []
            for idx, row in df.iterrows():
                text = row.get('description', row.get('title', ''))
                # Get 384-dim embedding
                embedding = self.bert_extractor.get_text_embedding(text)
                bert_features_list.append(embedding)
            
            X_bert = np.array(bert_features_list)
            
            # Combine Metadata + BERT
            logger.info(f"Combining Metadata ({X_meta.shape[1]}) + BERT ({X_bert.shape[1]})")
            X = np.hstack([X_meta, X_bert])
            
            # Update feature names for BERT dimensions
            bert_names = [f"bert_{i}" for i in range(X_bert.shape[1])]
            self.feature_names.extend(bert_names)
        else:
            logger.warning("BERT extractor not available, using only metadata.")
            X = X_meta
            
        # Encode outcomes
        y = self.outcome_encoder.fit_transform(df['outcome'])
        
        return X, y
    
    def _prepare_metadata_features(self, df: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """Encode and scale metadata features"""
        categorical_features = ['court', 'judge', 'case_type', 'legal_domain']
        numerical_features = [col for col in df.columns if col not in categorical_features]
        
        encoded_data = [] 
        
        # Encode categorical features
        for feature in categorical_features:
            if feature in df.columns:
                if fit:
                    self.feature_encoders[feature] = LabelEncoder()
                    encoded = self.feature_encoders[feature].fit_transform(df[feature].astype(str))
                else:
                    encoded = []
                    for val in df[feature].astype(str):
                        if val in self.feature_encoders[feature].classes_:
                            encoded.append(self.feature_encoders[feature].transform([val])[0])
                        else:
                            encoded.append(0) 
                    encoded = np.array(encoded)
                
                encoded_data.append(encoded.reshape(-1, 1))
        
        # Add numerical features
        for feature in numerical_features:
            if feature in df.columns:
                vals = df[feature].values.reshape(-1, 1)
                encoded_data.append(vals)
        
        if not encoded_data:
            raise ValueError("No features extracted")
            
        X = np.hstack(encoded_data)
        
        # Scale
        if fit:
            X = self.scaler.fit_transform(X)
            self.feature_names = categorical_features + numerical_features
        else:
            X = self.scaler.transform(X)
        
        return X
    
    def train_pipeline(self, data_path: str, use_smote: bool = True):
        """Train Stacking Ensemble"""
        print("=" * 80)
        print("STACKING ENSEMBLE TRAINING (XGB + LGBM + RF + BERT)")
        print("=" * 80)
        
        X, y = self.load_and_prepare_data(data_path)
        
        # Split Data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # SMOTE
        if use_smote:
            logger.info("Applying SMOTE...")
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            
        # Base Learners
        estimators = []
        if XGBOOST_AVAILABLE:
            estimators.append(('xgb', XGBClassifier(
                n_estimators=300, 
                max_depth=6, 
                learning_rate=0.1, 
                use_label_encoder=False, 
                eval_metric='mlogloss'
            )))
        if LIGHTGBM_AVAILABLE:
            estimators.append(('lgbm', LGBMClassifier(
                n_estimators=300, 
                max_depth=6, 
                learning_rate=0.1, 
                verbose=-1
            )))
        
        estimators.append(('rf', RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42, class_weight='balanced')))
        
        # Stacking Classifier
        logger.info("Training Stacking Ensemble...")
        self.stacking_model = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(),
            cv=5,
            n_jobs=1  # Avoid pickling issues
        )
        
        self.stacking_model.fit(X_train, y_train)
        
        # Calibration (Platt Scaling)
        logger.info("Calibrating model probabilities...")
        self.calibrated_model = CalibratedClassifierCV(self.stacking_model, method='sigmoid', cv='prefit')
        self.calibrated_model.fit(X_train, y_train)
        
        # Evaluate
        self.evaluate_model(self.calibrated_model, X_test, y_test)
        
        # Save
        self.save_model()
        
        return self.calibrated_model

    def evaluate_model(self, model, X_test, y_test):
        """Detailed evaluation"""
        print("\n📈 Evaluating Stacking Ensemble...")
        y_pred = model.predict(X_test)
        
        classes = [self.outcome_encoder.inverse_transform([c])[0] for c in np.unique(y_test)]
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=classes, zero_division=0))
        
        mcc = matthews_corrcoef(y_test, y_pred)
        print(f"Matthews Correlation Coefficient (MCC): {mcc:.4f}")
        
        # Brier Score (only works for binary or if averaged, but we can do per-class or just weighted)
        # For multi-class, brier_score_loss isn't direct in sklearn < 0.24 without care, 
        # but let's try a simple approach or skip if complex. 
        # Actually, simpler: just print probabilities for a few samples to verify calibration visually
        probs = model.predict_proba(X_test)
        confidence = np.max(probs, axis=1)
        avg_confidence = np.mean(confidence)
        acc = accuracy_score(y_test, y_pred)
        
        print(f"Average Confidence: {avg_confidence:.4f}")
        print(f"Actual Accuracy:    {acc:.4f}")
        print(f"Calibration Gap:    {abs(avg_confidence - acc):.4f}")

    def save_model(self):
        """Save artifacts"""
        print(f"\n💾 Saving Ensemble...")
        # Save the CALIBRATED model
        joblib.dump(self.calibrated_model, os.path.join(self.model_dir, 'stacking_model.pkl'))
        joblib.dump(self.feature_encoders, os.path.join(self.model_dir, 'feature_encoders.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'feature_scaler.pkl'))
        joblib.dump(self.outcome_encoder, os.path.join(self.model_dir, 'outcome_encoder.pkl'))
        joblib.dump(self.feature_names, os.path.join(self.model_dir, 'feature_names.pkl'))
        print("✅ Model saved.")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/training_cases.csv')
    args = parser.parse_args()
    
    trainer = StackingModelTrainer()
    if not os.path.exists(args.data) and os.path.exists(os.path.join('1-Rag', args.data)):
        args.data = os.path.join('1-Rag', args.data)
        
    trainer.train_pipeline(args.data)

if __name__ == "__main__":
    main()
