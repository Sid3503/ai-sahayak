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
                    **state.get("user_context", {}),
                    "target_language": detected_lang,
                    "requires_translation": True,
                    "original_content": last_message.content
                }
            }
            
        return {
            "user_context": {
                **state.get("user_context", {}),
                "target_language": detected_lang,
                "requires_translation": False
            }
        }

# For LangGraph node invocation
language_node_instance = LanguageRouterNode()
async def language_detection_node(state: ConversationState):
    return await language_node_instance.process_and_translate(state)
