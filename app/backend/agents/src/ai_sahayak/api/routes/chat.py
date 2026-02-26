import base64
import tempfile
import httpx
import os
from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from ai_sahayak.schemas.webhook import InboundPayload, OutboundPayload, ErrorResponse, WebhookAck
from ai_sahayak.memory.conversation import (
    get_conversation_state,
    save_conversation_state,
    restore_messages
)
from ai_sahayak.graphs.workflows.retail_assistant import graph

router = APIRouter()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def generate_suggested_actions(state: dict) -> list:
    """Generate suggested quick reply actions based on current state and language."""
    current_step = state.get("current_step", "")
    user_context = state.get("user_context", {})
    lang = user_context.get("target_language", "en")
    
    # Defaults
    if current_step == "wait_for_hi" or not current_step:
        if lang == "hi" or lang == "mr" or lang == "bn":
            return ["👋 नमस्ते (Hello)", "🗣️ English", "🗣️ Hindi / Hinglish"]
        return ["👋 Hello Sahayak", "🗣️ English", "🗣️ Hindi / Hinglish"]
        
    if current_step == "onboarding":
        if lang == "hi" or lang == "mr" or lang == "bn":
            return ["📞 मदद चाहिए (Help)"]
        return ["📞 Need Help"]

    if current_step == "completed":
        last_intent = state.get("next_intent", "default")
        
        if lang == "hi" or lang == "mr" or lang == "bn":
            dashboard_suggestions = {
                "sales_query": ["📈 आज की बिक्री", "📊 साप्ताहिक रिपोर्ट", "📉 पिछले महीने की बिक्री"],
                "pricing_query": ["💰 मूल्य विश्लेषण", "📊 प्रतियोगी कीमतें", "💡 मार्जिन टिप्स"],
                "inventory": ["📦 स्टॉक अलर्ट", "📋 इन्वेंटरी सारांश", "📊 स्टॉक स्तर"],
                "forecast": ["🎉 त्योहार का पूर्वानुमान", "📈 मांग भविष्यवाणी", "📊 मौसमी रुझान"],
                "default": ["💰 कीमत (Pricing)", "📦 स्टॉक (Inventory)", "📈 बिक्री (Sales)", "🎯 पूर्वानुमान (Forecast)"]
            }
        else:
            dashboard_suggestions = {
                "sales_query": ["📈 Today's Sales", "📊 Weekly Report", "📉 Month-over-Month"],
                "pricing_query": ["💰 Pricing Analysis", "📊 Competitor Rates", "💡 Margin Tips"],
                "inventory": ["📦 Restock Alert", "📋 Inventory Summary", "📊 Stock Levels"],
                "forecast": ["🎉 Festival Forecast", "📈 Demand Prediction", "📊 Seasonal Trends"],
                "default": ["💰 Pricing", "📦 Inventory", "📈 Sales", "🎯 Forecast"]
            }
        return dashboard_suggestions.get(last_intent, dashboard_suggestions["default"])
    
    return []

def _get_image_extension(media_type: str) -> str:
    """Get file extension from media type."""
    extensions = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    return extensions.get(media_type, ".jpg")

# ============================================================
# API ENDPOINTS
# ============================================================

@router.post("/webhook/incoming")
async def webhook_incoming(payload: InboundPayload):
    """
    Main webhook endpoint for receiving messages from Frontend Chat UI.
    """
    try:
        # Handle image processing
        if payload.image:
            try:
                image_data = base64.b64decode(payload.image)
                extension = _get_image_extension(payload.image_media_type or "image/jpeg")
                
                with tempfile.NamedTemporaryFile(
                    suffix=extension,
                    prefix="sahayak_image_",
                    delete=False
                ) as temp_file:
                    temp_file.write(image_data)
                    image_path = temp_file.name
                
                # In AI Sahayak, we might use this for Shelf Eye or SKU detection
                payload.text = f"[Image uploaded: {image_path}] " + (payload.text or "")
                
            except Exception as img_error:
                print(f"Error processing image: {img_error}")
                if not payload.text:
                    raise HTTPException(status_code=400, detail="Failed to process image")
        
        if not payload.text:
            raise HTTPException(status_code=400, detail="Either 'text' or 'image' must be provided")
        
        session_id = payload.session_id or f"{payload.platform}_{payload.user_id}"
        state = await get_conversation_state(session_id)
        
        # Restore messages
        if state.get("messages"):
            state["messages"] = restore_messages(state["messages"])
        
        # Add user message
        user_message = HumanMessage(content=payload.text, name=payload.user_id)
        state["messages"] = state.get("messages", []) + [user_message]
        
        # Add context from payload while preserving existing contextual flags
        current_context = state.get("user_context", {})
        state["user_context"] = {
            **current_context,
            "user_id": payload.user_id,
            "platform": payload.platform,
            "phone_number": payload.phone_number,
            **(payload.metadata or {})
        }

        # Invoke the LangGraph agent
        try:
            config = {"recursion_limit": 20}
            result = await graph.ainvoke(state, config=config)
        except Exception as graph_error:
            print(f"Graph invocation error: {graph_error}")
            result = {
                **state,
                "messages": state["messages"] + [AIMessage(content="I encountered an issue processing your request. How can I help you differently?")]
            }
        
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        reply_text = ai_messages[-1].content if ai_messages else "No response generated."
        
        # Determine if we need to translate the AI's English response back to the user's regional language
        user_context = result.get("user_context", {})
        if user_context.get("requires_translation"):
            from ai_sahayak.language.translation.pipeline import TranslationPipeline
            translator = TranslationPipeline()
            reply_text = await translator.translate_from_english(
                reply_text, 
                user_context.get("target_language", "hi")
            )
        
        # Save updated state
        await save_conversation_state(session_id, result)
        
        # Prepare response
        response_payload = OutboundPayload(
            user_id=payload.user_id,
            reply=reply_text,
            session_id=session_id,
            metadata={
                **(payload.metadata or {}),
                "current_step": result.get("current_step", "unknown"),
            },
            platform=payload.platform,
            suggested_actions=generate_suggested_actions(result)
        )
        
        # Async callback if requested
        if payload.callback_url:
            async with httpx.AsyncClient() as client:
                await client.post(payload.callback_url, json=response_payload.model_dump())
        
        return {
            "ok": True,
            "reply": reply_text,
            "session_id": session_id,
            "suggested_actions": response_payload.suggested_actions
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/outgoing")
async def webhook_outgoing_sink(data: OutboundPayload):
    """
    Sink for outgoing messages (useful for testing callbacks).
    """
    print(f"Outgoing message for {data.user_id}: {data.reply}")
    return {"status": "dispatched"}
