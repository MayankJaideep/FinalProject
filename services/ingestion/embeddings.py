from sentence_transformers import SentenceTransformer
from PIL import Image
import torch

class MultimodalEmbedder:
    def __init__(self, text_model_name="clip-ViT-B-32-multilingual-v1", image_model_name="clip-ViT-B-32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading text embedding model {text_model_name} on {self.device}...")
        try:
            self.text_model = SentenceTransformer(text_model_name, device=self.device)
        except Exception as e:
            print(f"Failed to load text model {text_model_name}: {e}")
            raise e

        print(f"Loading image embedding model {image_model_name} on {self.device}...")
        try:
            self.image_model = SentenceTransformer(image_model_name, device=self.device)
        except Exception as e:
            print(f"Failed to load image model {image_model_name}: {e}")
            raise e

    def embed_text(self, text: str):
        return self.text_model.encode(text)

    def embed_image(self, image: Image.Image):
        # Use simple model.encode(image) as standard CLIP model supports it.
        # Wrap in LIST to be safe based on previous debugging, but standard CLIP might work with single.
        # Let's try single first, or safe list. Safe list is better.
        try:
            # Check if image is valid
            if image.mode != "RGB":
                image = image.convert("RGB")
                
            embeddings = self.image_model.encode(image)
            return embeddings
        except Exception as e:
            print(f"Error embedding image: {e}")
            raise e

    def embed_batch_texts(self, texts: list):
        return self.text_model.encode(texts)

    def embed_batch_images(self, images: list):
        return self.image_model.encode(images)
