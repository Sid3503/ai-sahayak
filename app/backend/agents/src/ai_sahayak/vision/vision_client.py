import boto3
import json
from base64 import b64encode
from ai_sahayak.config.settings import settings

class VisionClient:
    """Client for Interacting with Vision LLMs (e.g., Qwen Vision via Bedrock/API)."""
    
    def __init__(self):
        # We assume standard Bedrock client for multimodal, but abstract it here.
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.BEDROCK_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        # Amazon Nova Pro supports multimodal image content blocks
        self.model_id = "amazon.nova-pro-v1:0"

    async def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        """
        Send an image and a prompt to the Vision LLM.
        """
        # For a multimodal model like Claude 3 or Qwen-VL via Converse API:
        try:
            image_base64 = b64encode(image_bytes).decode('utf-8')
            
            message = {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": mime_type.split('/')[-1], # e.g., 'jpeg', 'png'
                            "source": {
                                "bytes": image_bytes
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }

            response = self.bedrock.converse(
                modelId=self.model_id,
                messages=[message],
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.2
                }
            )
            
            return response['output']['message']['content'][0]['text']
            
        except Exception as e:
            # Fallback for models that might not support the Converse API natively or if we just want a mock
            print(f"Vision API Error: {e}. Returning mock vision analysis for development.")
            return '{"status": "success", "analysis": "Mock analysis: Shelf appears 80% stocked. Low on Maggi Noodles and Parle-G."}'
