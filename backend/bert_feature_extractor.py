"""
BERT-based Feature Extractor for Legal Text.
Uses 'law-ai/InLegalBERT' (768d) to generate dense vector embeddings that capture semantic meaning.
"""

import numpy as np
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Identify if Mac ARM for hardware acceleration
mac_device = "mps" if platform.system() == "Darwin" and platform.machine() == "arm64" else "cpu"

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not installed. Using fallback zeros.")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class BERTFeatureExtractor:
    """Extracts semantic embeddings using a pre-trained Transformer model"""
    
    def __init__(self, model_name='law-ai/InLegalBERT'):
        """
        Initialize with a specific model.
        Default: 'law-ai/InLegalBERT' (State-of-the-art for Indian Law)
        """
        self.model = None
        self.embedding_dim = 768 # InLegalBERT is 768d
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"🔄 Loading SentenceTransformer model: {model_name} on {mac_device}...")
                self.model = SentenceTransformer(model_name, device=mac_device)
                logger.info("✅ Model loaded successfully.")
                
                # Verify dimension
                test_emb = self.model.encode("test")
                self.embedding_dim = len(test_emb)
                logger.info(f"ℹ️ Embedding Dimension: {self.embedding_dim}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                logger.info("Falling back to standard 'all-MiniLM-L6-v2'...")
                try:
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                    self.embedding_dim = 384
                except:
                    pass
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for the input text.
        
        Args:
            text: Case description or summary.
            
        Returns:
            numpy array of shape (768,) or (384,) depending on model.
        """
        if not self.model:
            # Return zero vector if model is missing (fallback)
            return np.zeros(self.embedding_dim)
            
        try:
            # Encode text (convert to numpy automatically)
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return np.zeros(self.embedding_dim)

# Singleton instance for easy import
bert_extractor = BERTFeatureExtractor()
