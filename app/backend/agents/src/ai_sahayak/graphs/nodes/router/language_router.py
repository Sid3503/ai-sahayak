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
        # If there are no messages, default to english
        if not state["messages"]:
            return {"user_context": {**state.get("user_context", {}), "target_language": "en"}}
            
        last_message = state["messages"][-1]
        
        # Only process if it is a human message
        if not isinstance(last_message, HumanMessage):
             return {"user_context": {**state.get("user_context", {}), "target_language": "en"}}
             
        if not last_message.content:
            return {"user_context": {**state.get("user_context", {}), "target_language": "en"}}
            
        detected_lang = self.detector.detect(last_message.content)
        user_context = state.get("user_context", {})
        prev_lang = user_context.get("target_language", "en")
        
        # If the user previously selected a non-English language and just typed a short word or filename (which detects as EN)
        # we should preserve their original language preference instead of snapping back to English forever.
        if detected_lang == "en" and prev_lang != "en" and len(last_message.content.split()) < 5:
            # Assume it's a short reply in the established language context
            target_lang = prev_lang
        else:
            target_lang = detected_lang
            
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
                    "target_language": target_lang,
                    "requires_translation": True,
                    "original_content": last_message.content
                }
            }
            
        return {
            "user_context": {
                **user_context,
                "target_language": target_lang,
                "requires_translation": (target_lang != "en")
            }
        }

# For LangGraph node invocation
language_node_instance = LanguageRouterNode()
async def language_detection_node(state: ConversationState):
    return await language_node_instance.process_and_translate(state)
