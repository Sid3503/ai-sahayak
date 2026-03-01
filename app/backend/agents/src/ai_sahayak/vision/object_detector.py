from typing import Dict, Any, List
from .vision_client import VisionClient
from .image_processor import ImageProcessor

class ObjectDetector:
    """Specialized component for identifying specific items in an image (e.g., specific brand SKUs)."""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.vision_client = VisionClient()

    async def detect_objects(self, base64_image: str, target_objects: List[str] = None, mime_type: str = None) -> Dict[str, Any]:
        """Detect specific objects or brands in an uploaded image."""
        try:
            image_bytes, format_type = self.processor.validate_and_decode(base64_image, mime_type)
            
            targets = ", ".join(target_objects) if target_objects else "any recognizable retail products"
            
            prompt = f"""
            Identify these specific objects in the image: {targets}.
            Return the results as a JSON list of objects found, with bounding box approximations or just counts.
            """
            
            # For Phase 5 MVP, we just do a generic query 
            raw_analysis = await self.vision_client.analyze_image(image_bytes, format_type, prompt)
            
            return {
                "status": "success",
                "raw_detection": raw_analysis
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
