import base64
import tempfile
import httpx
import os
from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from ai_sahayak.schemas.webhook import InboundPayload, OutboundPayload, ErrorResponse, WebhookAck
from ai_sahayak.graphs.workflows.retail_assistant import graph
from ai_sahayak.memory.conversation import save_conversation_state

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
        return []

    if current_step == "completed":
        # Don't show Pricing/Inventory/Sales buttons for web demo users
        # Only show them for known retailers with actual dashboard data
        return []
    
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
    Supports text, image, and audio (voice message → Amazon Transcribe → text).
    """
    try:
        image_path = None
        transcribed_text = None

        # Handle voice message: transcribe audio to text (Amazon Transcribe)
        if payload.audio:
            from ai_sahayak.tools.transcribe import transcribe_audio
            lang = (payload.metadata or {}).get("voice_language", "hi")
            language_code = "hi-IN" if lang in ("hi", "mr", "bn") else "en-IN"
            transcribed_text = transcribe_audio(
                payload.audio,
                media_type=payload.audio_media_type or "audio/webm",
                language_code=language_code,
            )
            if transcribed_text:
                payload.text = transcribed_text
            else:
                payload.text = payload.text or "Voice message"

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
            raise HTTPException(status_code=400, detail="Either 'text', 'image', or 'audio' (voice) must be provided")
        
        session_id = payload.session_id or f"{payload.platform}_{payload.user_id}"
        user_message = HumanMessage(content=payload.text, name=payload.user_id)
        
        print(f"--- Chat Route Triggered: {session_id} ---")
        # Load previous conversation history manually
        from ai_sahayak.memory.conversation import get_conversation_state, restore_messages
        print("Fetching conversation state...")
        prior_state = await get_conversation_state(session_id)
        print("State fetched successfully.")
        
        # Live Alerts / My day: skip onboarding so user gets normal chat (English/Hinglish/Hindi), not the 7-question flow.
        # session_id from frontend is "day-session-{retailerKey}" (e.g. day-session-raju); user_id is the retailer key.
        if session_id.startswith("day-session-") and (
            not prior_state.get("messages") or prior_state.get("current_step") in ("onboarding", "wait_for_hi", "")
        ):
            uid = (payload.user_id or "").strip().lower()
            prior_state["current_step"] = "completed"
            prior_state.setdefault("onboarding_data", {})
            if uid and not prior_state["onboarding_data"].get("name"):
                prior_state["onboarding_data"]["name"] = uid.capitalize()
            prior_state["onboarding_data"].setdefault("preferred_language", "English")
        
        # Restore messages and append new one
        restored_messages = restore_messages(prior_state.get("messages", []))
        restored_messages.append(user_message)
        print(f"Messages restored. Count: {len(restored_messages)}")
        
        # Prepare inputs merging old state and new context
        inputs = prior_state.copy()
        inputs["messages"] = restored_messages
        inputs["user_context"] = {
            "user_id": payload.user_id,
            "platform": payload.platform,
            "phone_number": payload.phone_number,
            **(payload.metadata or {})
        }
        
        if image_path:
            inputs["image_path"] = image_path
            
        # Invoke the LangGraph agent statelessly
        try:
            config = {
                "recursion_limit": 20,
                "configurable": {
                    "actor_id": payload.user_id,
                    "thread_id": f"wa-{session_id}"[:80]
                }
            }
            # graph.ainvoke is now stateless as we manage input state manually
            result = await graph.ainvoke(inputs, config=config)
        except Exception as graph_error:
            print(f"Graph invocation error: {graph_error}")
            # Fallback result to allow replying even on failure
            result = {
                **inputs,
                "messages": [AIMessage(content="I encountered an issue processing your request. How can I help you differently?")]
            }
        
        ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
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
        
        # After onboarding credentials message, don't show Pricing/Inventory/Sales — only the ID/pass and "Open Dashboard" flow
        suggested = generate_suggested_actions(result)
        if ("User ID:" in reply_text or "Your Sahayak Analytics Dashboard Login" in reply_text) and result.get("current_step") == "completed":
            suggested = []

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
            suggested_actions=suggested
        )
        
        # Async callback if requested
        if payload.callback_url:
            async with httpx.AsyncClient() as client:
                await client.post(payload.callback_url, json=response_payload.model_dump())
                
        # Save readable conversation history to DynamoDB for dashboard/admin use
        try:
            state_to_save = dict(result)
            await save_conversation_state(session_id, state_to_save)
        except Exception as e:
            print(f"Failed to save conversation history: {e}")
        
        out = {
            "ok": True,
            "reply": reply_text,
            "session_id": session_id,
            "suggested_actions": response_payload.suggested_actions,
        }
        if transcribed_text is not None:
            out["transcribed_text"] = transcribed_text
        return out
        
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
