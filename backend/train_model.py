"""
Train Improved ML Model (Stacking Ensemble) with Optuna Optimization & InLegalBERT
"""

import pandas as pd
import numpy as np
import joblib
import os
import argparse
import logging
from typing import Dict, Any, List

# ML Libraries
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, matthews_corrcoef, brier_score_loss, log_loss

# Ensembles
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Balancing
from imblearn.over_sampling import SMOTE

# Optimization
import optuna

# Custom
try:
    from bert_feature_extractor import bert_extractor
except ImportError:
    bert_extractor = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalOutcomeTrainer:
    def __init__(self, data_path: str, model_dir: str = "models"):
        self.data_path = data_path
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # State
        self.df = None
        self.X = None
        self.y = None
        self.encoder = None
        self.scaler = None
        self.feature_encoders = {}
        self.best_params = {}
        
    def load_and_clean_data(self):
        """Load data, handle new structured columns"""
        logger.info(f"📂 Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        
        # Standardize Outcome
        self.df['outcome'] = self.df['outcome'].str.lower().str.strip()
        valid_outcomes = ['allowed', 'dismissed', 'settlement', 'partly_allowed']
        self.df = self.df[self.df['outcome'].isin(valid_outcomes)]
        
        # --- FEATURE ENGINEERING (New rich features) ---
        # Fill missing new columns if working with mixed data
        new_cols = ['lower_court_decision', 'petitioner_type', 'main_statute']
        for col in new_cols:
            if col not in self.df.columns:
                self.df[col] = 'unknown'
            else:
                self.df[col] = self.df[col].fillna('unknown').str.lower()
        
        logger.info(f"✅ Data Loaded. Shape: {self.df.shape}")
        
    def extract_features(self):
        """Combine Metadata + Structured Features + BERT"""
        
        # 1. Categorical Encoders
        cat_features = ['court', 'judge', 'case_type', 'lower_court_decision', 'petitioner_type']
        # Note: 'main_statute' might be too high cardinality, treat as text or top-N?
        # For now, let's skip statute categorical encoding to avoid sparsity, reliance on BERT for it.
        
        encoded_metas = []
        feature_names = []
        
        for col in cat_features:
            if col in self.df.columns:
                le = LabelEncoder()
                # Handle unknown
                self.df[col] = self.df[col].fillna('unknown').astype(str)
                encoded_cols = le.fit_transform(self.df[col])
                encoded_metas.append(encoded_cols.reshape(-1, 1))
                self.feature_encoders[col] = le
                feature_names.append(col)
                
        X_meta = np.hstack(encoded_metas)
        
        # 2. BERT Embeddings
        logger.info("🧠 Generating InLegalBERT Embeddings...")
        if bert_extractor:
            # Use 'description' or fall back to 'title' if available
            if 'title' in self.df.columns:
                texts = self.df['description'].fillna(self.df['title']).tolist()
            else:
                texts = self.df['description'].fillna("").tolist()
            
            embeddings = bert_extractor.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            logger.info(f"   Shape: {embeddings.shape}")
        else:
            embeddings = np.zeros((len(self.df), 384)) # Fallback
            
        # Combine
        self.X = np.hstack([X_meta, embeddings])
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(self.X)
        
        # Encode Target
        self.encoder = LabelEncoder()
        self.y = self.encoder.fit_transform(self.df['outcome'])
        
        # Save feature names for inference
        joblib.dump(feature_names, os.path.join(self.model_dir, 'feature_names.pkl'))
        
        logger.info(f"✅ Features Ready. X: {self.X.shape}")

    def optimize_xgboost(self, X_train, y_train):
        """Use Optuna to find best XGBoost params"""
        logger.info("🔬 Starting Optuna Optimization for XGBoost...")
        
        def objective(trial):
            param = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'eval_metric': 'mlogloss',
                'n_jobs': -1
            }
            
            clf = XGBClassifier(**param)
            # Stratified CV for stability
            scores = cross_val_score(clf, X_train, y_train, cv=3, scoring='accuracy')
            return scores.mean()

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=10) # 10 trials to be fast, increase for 90%
        
        logger.info(f"   Best Params: {study.best_params}")
        return XGBClassifier(**study.best_params)

    def train_pipeline(self):
        # Split
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42, stratify=self.y)
        
        # Balance
        smote = SMOTE(random_state=42)
        X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
        
        # Base Learners
        # 1. Optimized XGBoost
        xgb_optimized = self.optimize_xgboost(X_train_bal, y_train_bal)
        
        # 2. LightGBM
        lgbm = LGBMClassifier(n_estimators=150, learning_rate=0.05)
        
        # 3. Random Forest (Robust Baseline)
        rf = RandomForestClassifier(n_estimators=200, max_depth=10)
        
        estimators = [
            ('xgb', xgb_optimized),
            ('lgbm', lgbm),
            ('rf', rf)
        ]
        
        # Stacking
        logger.info("🏗️ Building Stacking Ensemble...")
        stack_clf = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(),
            cv=3
        )
        
        # Calibration (Platt Scaling)
        self.calibrated_model = CalibratedClassifierCV(stack_clf, method='sigmoid', cv=3)
        self.calibrated_model.fit(X_train_bal, y_train_bal)
        
        # Evaluate
        self.evaluate(X_test, y_test)
        
        # Save
        self.save_model()

    def evaluate(self, X_test, y_test):
        y_pred = self.calibrated_model.predict(X_test)
        y_prob = self.calibrated_model.predict_proba(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        mcc = matthews_corrcoef(y_test, y_pred)
        
        logger.info(f"\n📊 --- FINAL RESULTS ---")
        logger.info(f"   Accuracy: {acc:.2%}")
        logger.info(f"   MCC Score: {mcc:.4f}")
        logger.info("\n" + classification_report(y_test, y_pred, target_names=self.encoder.classes_))

    def save_model(self):
        joblib.dump(self.calibrated_model, os.path.join(self.model_dir, 'stacking_model.pkl'))
        joblib.dump(self.feature_encoders, os.path.join(self.model_dir, 'feature_encoders.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'feature_scaler.pkl'))
        joblib.dump(self.encoder, os.path.join(self.model_dir, 'outcome_encoder.pkl'))
        logger.info("💾 Model Artifacts Saved.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="1-Rag/data/cleaned_training_data.csv")
    args = parser.parse_args()
    
    trainer = LegalOutcomeTrainer(args.data)
    trainer.load_and_clean_data()
    trainer.extract_features()
    trainer.train_pipeline()
