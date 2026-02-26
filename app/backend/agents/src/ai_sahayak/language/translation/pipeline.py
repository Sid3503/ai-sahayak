from .bhashini_client import BhashiniClient
from ai_sahayak.tools.llm.bedrock_client import get_llm
from langchain_core.messages import SystemMessage

class TranslationPipeline:
    def __init__(self):
        self.bhashini_client = BhashiniClient()
        self.llm = get_llm(temperature=0.1)
        
    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate from regional language to English"""
        try:
            return await self.bhashini_client.translate(text, source_lang, "en")
        except Exception:
            # Fallback to LLM translation
            return await self._llm_translate(text, source_lang, "en")
            
    async def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate from English to regional language"""
        try:
            return await self.bhashini_client.translate(text, "en", target_lang)
        except Exception:
            return await self._llm_translate(text, "en", target_lang)
            
    async def _llm_translate(self, text: str, source: str, target: str) -> str:
        prompt = f"""Translate this text from {source} to {target}:
        {text}
        
        Only respond with the translated text."""
        
        response = await self.llm.ainvoke([SystemMessage(content=prompt)])
        return response.content
