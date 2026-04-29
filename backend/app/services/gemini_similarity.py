import os
from pathlib import Path
import google.generativeai as genai
from PIL import Image

from .embedding_store import (
    SimilarityServiceError,
    cosine_similarity,
    load_embedding_store,
    save_embedding_store,
)

class GeminiSimilarityService:
    def __init__(self, api_key, store_path):
        if not api_key:
            raise ValueError("Gemini similarity requires a GEMINI_API_KEY.")

        self.api_key = api_key
        self.store_path = Path(store_path)
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        self.embedding_model = 'models/text-embedding-004'

    def embedding_for_image(self, image_path):
        try:
            img = Image.open(image_path)
            
            # Step 1: Extract a rich dense visual description
            prompt = (
                "Describe the visual elements of this image in extreme detail. "
                "Focus on objects, colors, text, unique identifiable marks, "
                "composition, and overall scene. This description will be used "
                "to find exact duplicates or highly similar images, so be as "
                "precise as possible."
            )
            response = self.vision_model.generate_content([prompt, img])
            description = response.text
            
            if not description:
                raise SimilarityServiceError("Gemini failed to generate a description for the image.")

            # Step 2: Embed the description into a 768-dimensional vector
            embedding_response = genai.embed_content(
                model=self.embedding_model,
                content=description,
                task_type="retrieval_document"
            )
            
            return embedding_response['embedding']
        except Exception as exc:
            raise SimilarityServiceError(
                f"Failed to generate Gemini image embedding: {str(exc)}"
            ) from exc

    def compare_against_store(self, image_path):
        records = load_embedding_store(self.store_path)
        if not records:
            return {
                "similarity": 0.0,
                "best_match": None,
                "matches": [],
            }

        embedding = self.embedding_for_image(image_path)
        matches = []

        for record in records:
            similarity = cosine_similarity(embedding, record["embedding"])
            # Scale up Gemini text cosine similarities slightly since text similarity 
            # bounds are generally narrower than direct image vector bounds
            # For Gemini embedding 004, typical unrelated text is ~0.5, highly related is ~0.8-0.9+
            scaled_similarity = max(0.0, min(100.0, (similarity - 0.5) * 200.0))
            
            matches.append(
                {
                    "id": record["id"],
                    "owner": record["owner"],
                    "similarity": scaled_similarity,
                }
            )

        matches.sort(key=lambda item: item["similarity"], reverse=True)
        best_match = matches[0] if matches else None

        return {
            "similarity": best_match["similarity"] if best_match else 0.0,
            "best_match": best_match,
            "matches": matches,
        }

    def store_embedding(self, image_path, item_id, owner="Unverified"):
        embedding = self.embedding_for_image(image_path)
        records = load_embedding_store(self.store_path)
        filtered = [record for record in records if record["id"] != str(item_id)]
        filtered.append(
            {
                "id": str(item_id),
                "owner": str(owner or "Unverified"),
                "embedding": embedding,
            }
        )
        save_embedding_store(self.store_path, filtered)
        return True
