import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import config

class VisualSearchEngine:
    def __init__(self):
        print("Loading Multimodal CLIP Model...")
        self.model = SentenceTransformer(config.CLIP_MODEL_NAME)
        self.image_paths = []
        self.image_embeddings = None
        
    def index_images(self):
        if not os.path.exists(config.IMAGE_DIR):
            raise FileNotFoundError(f"Missing image directory: {config.IMAGE_DIR}")
            
        valid_exts = ('.jpg', '.jpeg', '.png')
        self.image_paths = [
            os.path.join(config.IMAGE_DIR, f) 
            for f in os.listdir(config.IMAGE_DIR) 
            if f.lower().endswith(valid_exts)
        ]
        
        if not self.image_paths:
            return 0
            
        print(f"Encoding {len(self.image_paths)} images into vectors...")
        
        images = []
        for path in self.image_paths:
            try:
                images.append(Image.open(path).convert("RGB"))
            except Exception as e:
                print(f"Skipping {path}: {e}")
                
        self.image_embeddings = self.model.encode(images, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        print("✅ Image Indexing Complete!")
        return len(self.image_paths)

    def search(self, query, top_k=8):
        """Searches using TEXT."""
        if not self.image_paths or self.image_embeddings is None:
            return []
            
        text_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(text_embedding, self.image_embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.image_paths)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            results.append({
                "image_path": self.image_paths[idx.item()],
                "score": score.item() * 100,
                "filename": os.path.basename(self.image_paths[idx.item()])
            })
        return results

    def search_by_image(self, uploaded_image, top_k=8):
        """Searches using an UPLOADED IMAGE (Reverse Search)."""
        if not self.image_paths or self.image_embeddings is None:
            return []
            
        # Convert uploaded file to PIL Image
        img = Image.open(uploaded_image).convert("RGB")
        
        # Embed the uploaded image
        query_embedding = self.model.encode(img, convert_to_tensor=True)
        
        # Compare with database
        cos_scores = util.cos_sim(query_embedding, self.image_embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.image_paths)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            results.append({
                "image_path": self.image_paths[idx.item()],
                "score": score.item() * 100,
                "filename": os.path.basename(self.image_paths[idx.item()])
            })
        return results