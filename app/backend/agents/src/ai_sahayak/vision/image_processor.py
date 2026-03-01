import base64
import io
import mimetypes
from typing import Tuple, Optional

class ImageProcessor:
    """Handles parsing, validation, and preprocessing of images for Vision APIs."""
    
    SUPPORTED_FORMATS = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
    
    @staticmethod
    def validate_and_decode(base64_string: str, mime_type: Optional[str] = None) -> Tuple[bytes, str]:
        """
        Validates and decodes a base64 string into bytes.
        Returns a tuple of (image_bytes, mime_type).
        """
        try:
            # Handle Data URI scheme if present (e.g., "data:image/jpeg;base64,...")
            if base64_string.startswith('data:'):
                prefix, base64_string = base64_string.split(',', 1)
                if not mime_type:
                    mime_type = prefix.split(';')[0].replace('data:', '')
            
            image_bytes = base64.b64decode(base64_string)
            
            if len(image_bytes) > ImageProcessor.MAX_SIZE_BYTES:
                raise ValueError(f"Image exceeds maximum size of {ImageProcessor.MAX_SIZE_BYTES / 1024 / 1024}MB")
                
            if not mime_type:
                # Basic magic number checking as a fallback
                if image_bytes.startswith(b'\xff\xd8'):
                    mime_type = 'image/jpeg'
                elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                    mime_type = 'image/png'
                elif image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP':
                    mime_type = 'image/webp'
                else:
                    mime_type = 'application/octet-stream'
            
            if mime_type not in ImageProcessor.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported image format: {mime_type}. Supported formats: {ImageProcessor.SUPPORTED_FORMATS}")
                
            return image_bytes, mime_type
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
            
    @staticmethod
    def encode_to_base64(image_bytes: bytes) -> str:
        """Encodes image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode('utf-8')
