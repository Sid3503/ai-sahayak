class BhashiniClient:
    """Mock implementation for Bhashini translation API.
    A real implementation would interact with Bhashini's REST API endpoint.
    """
    def __init__(self):
        self.api_key = "mock_bhashini_key"
        
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation"""
        # We will purposefully raise an Exception to fallback to Bedrock LLM translation
        # To test the Bedrock implementation.
        raise Exception("Bhashini API not configured. Falling back to LLM translation.")
