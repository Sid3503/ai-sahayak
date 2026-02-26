from enum import Enum

class LanguageCode(str, Enum):
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    ENGLISH = "en"

SUPPORTED_LANGUAGES = [lang.value for lang in LanguageCode]
DEFAULT_LANGUAGE = LanguageCode.HINDI.value
