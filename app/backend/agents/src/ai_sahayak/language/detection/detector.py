from lingua import LanguageDetectorBuilder, Language
import re

class LanguageDetector:
    SUPPORTED_LANGUAGES = {
        "en": Language.ENGLISH,
        "hi": Language.HINDI,
        "mr": Language.MARATHI,
        "bn": Language.BENGALI,
        "ta": Language.TAMIL,
        "te": Language.TELUGU
    }
    
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_all_languages().build()
        
    def detect(self, text: str) -> str:
        """Detect language with confidence threshold"""
        if not text.strip():
            return "en"
            
        # Clean text for better detection
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        
        confidence_scores = self.detector.compute_language_confidence_values(clean_text)
        
        if confidence_scores and confidence_scores[0].value > 0.7:
            detected_lang = confidence_scores[0].language
            return next((code for code, lang in self.SUPPORTED_LANGUAGES.items() 
                        if lang == detected_lang), "en")
        
        return "en"
