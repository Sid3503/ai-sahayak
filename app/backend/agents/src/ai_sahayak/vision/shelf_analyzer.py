from typing import Dict, Any, List
import json
from .image_processor import ImageProcessor
from .vision_client import VisionClient

class ShelfAnalyzer:
    """Orchestrates image processing and vision analysis for inventory assessment."""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.vision_client = VisionClient()
        
    async def analyze_shelf_image(self, base64_image: str, mime_type: str = None) -> Dict[str, Any]:
        """
        Takes a base64 encoded image, processes it, and analyzes stock levels.
        Returns structured data about the shelf.
        """
        try:
            # 1. Parse and validate image
            image_bytes, format_type = self.processor.validate_and_decode(base64_image, mime_type)
            
            # 2. Construct specific prompt for Shelf Eye
            prompt = """
            Analyze this shelf image for a retail store. Identify the visible products and estimate stocking levels.
            Provide your response STRICTLY as a JSON object matching this schema:
            {
               "status": "success",
               "insights": {
                   "overall_stock_level": "High/Medium/Low",
                   "empty_spaces_detected": true/false,
                   "categories_identified": ["snack", "beverage", etc]
               },
               "inventory_updates": [
                   {"product": "product_name", "estimated_count": integer, "status": "adequate/low/out_of_stock"}
               ]
            }
            Do not include Markdown blocks. Just return the JSON.
            """
            
            # 3. Call Vision Model
            raw_analysis = await self.vision_client.analyze_image(image_bytes, format_type, prompt)
            
            # 4. Parse response
            try:
                # Basic cleanup if model wrapped it in markdown
                if "```json" in raw_analysis:
                    raw_analysis = raw_analysis.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_analysis:
                    raw_analysis = raw_analysis.split("```")[1].strip()
                    
                parsed_data = json.loads(raw_analysis)
                return parsed_data
            except json.JSONDecodeError:
                # Mock fallback if JSON parsing fails
                print(f"Failed to parse vision response as JSON: {raw_analysis}")
                return {
                    "status": "partial_success",
                    "raw_text": raw_analysis,
                    "insights": {"overall_stock_level": "Unknown", "empty_spaces_detected": False, "categories_identified": []},
                    "inventory_updates": []
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
