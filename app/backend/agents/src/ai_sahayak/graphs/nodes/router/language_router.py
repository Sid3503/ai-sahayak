from typing import Literal
from ai_sahayak.language.detection.detector import LanguageDetector
from ai_sahayak.language.translation.pipeline import TranslationPipeline
from ai_sahayak.graphs.state.conversation import ConversationState
from langchain_core.messages import HumanMessage

class LanguageRouterNode:
    def __init__(self):
        self.detector = LanguageDetector()
        self.translator = TranslationPipeline()
        
    async def process_and_translate(self, state: ConversationState) -> dict:
        """Detect language and prepare translated content"""
        user_context = state.get("user_context", {}) or {}
        onboarding_data = state.get("onboarding_data", {}) or {}
        current_step = state.get("current_step", "")

        # If user already chose a language during onboarding, never override it (same flow as English, just different reply language)
        preferred = (onboarding_data.get("preferred_language") or "").strip().lower()
        if preferred and current_step in ("onboarding", "", "wait_for_hi"):
            lang_code = "en" if preferred == "english" else "hi" if preferred in ("hindi", "hinglish") else "mr" if preferred == "marathi" else "en"
            return {
                "user_context": {
                    **user_context,
                    "target_language": lang_code,
                    "requires_translation": (lang_code != "en"),
                }
            }

        # If the user's message is exactly a language choice (e.g. "Hindi", "Hinglish"), set target_language and do NOT translate the message
        last_content = ""
        if state.get("messages"):
            last_msg = state["messages"][-1]
            if isinstance(last_msg, HumanMessage) and getattr(last_msg, "content", None):
                last_content = str(last_msg.content).strip().lower()
        if last_content in ("english", "hindi", "hinglish", "marathi"):
            lang_code = "en" if last_content == "english" else "hi" if last_content in ("hindi", "hinglish") else "mr"
            return {
                "user_context": {
                    **user_context,
                    "target_language": lang_code,
                    "requires_translation": (lang_code != "en"),
                }
            }

        # If there are no messages, default to english
        if not state["messages"]:
            return {"user_context": {**user_context, "target_language": "en"}}
            
        last_message = state["messages"][-1]
        
        # Only process if it is a human message
        if not isinstance(last_message, HumanMessage):
             return {"user_context": {**user_context, "target_language": user_context.get("target_language", "en")}}
             
        if not last_message.content:
            return {"user_context": {**user_context, "target_language": user_context.get("target_language", "en")}}
            
        detected_lang = self.detector.detect(last_message.content)
        prev_lang = user_context.get("target_language", "en")
        # During onboarding, preserve user's chosen language for short replies (e.g. name, store name)
        if current_step == "onboarding" and prev_lang and len(str(last_message.content).split()) < 6:
            if detected_lang != prev_lang:
                detected_lang = prev_lang
        
        if detected_lang != "en":
            # Translate input to English for processing
            translated_input = await self.translator.translate_to_english(
                last_message.content, detected_lang
            )
            # Create a new list with modified last message so we don't accidentally mutate in-place if restricted
            modified_message_list = state["messages"].copy()
            # Replace the last message with one that contains translation details
            modified_message_list[-1] = HumanMessage(
                content=f"[{detected_lang.upper()}] {translated_input}",
                name=last_message.name
            )
            return {
                "messages": modified_message_list,
                "user_context": {
                    **user_context,
                    "target_language": detected_lang,
                    "requires_translation": True,
                    "original_content": last_message.content
                }
            }
            
        return {
            "user_context": {
                **user_context,
                "target_language": detected_lang,
                "requires_translation": False
            }
        }

# For LangGraph node invocation
language_node_instance = LanguageRouterNode()
async def language_detection_node(state: ConversationState):
    return await language_node_instance.process_and_translate(state)
