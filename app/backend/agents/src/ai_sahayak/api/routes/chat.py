import asyncio
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
        session_id = payload.session_id or f"{payload.platform}_{payload.user_id}"

        # Handle voice message: transcribe audio to text (Amazon Transcribe)
        if payload.audio:
            from ai_sahayak.tools.transcribe import transcribe_audio
            from ai_sahayak.memory.conversation import get_conversation_state
            # Use user's chosen language so transcript matches (English → Latin script, Hindi → Devanagari)
            prior = await get_conversation_state(session_id)
            preferred = (prior.get("onboarding_data") or {}).get("preferred_language") or ""
            if preferred and preferred.lower() in ("hindi", "hinglish"):
                language_code = "hi-IN"
            else:
                language_code = "en-IN"
            print(f"[Chat] Voice message received, transcribing (lang={language_code}, preferred={preferred or 'none'})...")
            try:
                transcribed_text = await asyncio.to_thread(
                    transcribe_audio,
                    payload.audio,
                    payload.audio_media_type or "audio/webm",
                    language_code,
                )
            except Exception as e:
                print(f"[Chat] Transcribe error: {e}")
                transcribed_text = None
            if transcribed_text:
                print(f"[Chat] Transcribe result: {transcribed_text[:80]}...")
                payload.text = transcribed_text
            else:
                print("[Chat] Transcribe returned None — using placeholder")
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

        user_message = HumanMessage(content=payload.text, name=payload.user_id)
        
        print(f"--- Chat Route Triggered: {session_id} ---")
        # Load previous conversation history manually
        from ai_sahayak.memory.conversation import get_conversation_state, restore_messages
        print("Fetching conversation state...")
        prior_state = await get_conversation_state(session_id)
        print("State fetched successfully.")
        
        # Live Alerts / My day: skip onboarding and always use Hinglish for shopkeepers.
        # session_id from frontend is "day-session-{retailerKey}" (e.g. day-session-raju); user_id is the retailer key.
        if session_id.startswith("day-session-"):
            prior_state.setdefault("onboarding_data", {})
            prior_state["onboarding_data"]["preferred_language"] = "Hinglish"
            if (
                not prior_state.get("messages") or prior_state.get("current_step") in ("onboarding", "wait_for_hi", "")
            ):
                uid = (payload.user_id or "").strip().lower()
                prior_state["current_step"] = "completed"
                if uid and not prior_state["onboarding_data"].get("name"):
                    prior_state["onboarding_data"]["name"] = uid.capitalize()
        
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
            import traceback
            print(f"Graph invocation error: {graph_error}")
            print(traceback.format_exc())
            # Fallback so user always gets a reply (onboarding or post-onboarding)
            fallback_msg = (
                "Sorry, something went wrong on my side. Please try again in a moment, or rephrase your message."
            )
            result = {
                **inputs,
                "messages": [AIMessage(content=fallback_msg)],
            }
        ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
        reply_text = (ai_messages[-1].content if ai_messages else "").strip() or "I didn't catch that. Could you repeat?"

        # Translate reply only when user chose Hindi (Devanagari). Hinglish: LLM replies in Hinglish via prompt; no translation.
        # Never translate the credentials message — User ID and Password must stay in Latin so user can sign in.
        user_context = result.get("user_context", {})
        onboarding_data = result.get("onboarding_data", {}) or {}
        preferred = (onboarding_data.get("preferred_language") or "").strip().lower()
        target_lang = user_context.get("target_language", "en")
        is_credentials_message = "User ID:" in reply_text and "Password:" in reply_text
        if preferred == "hindi" and target_lang != "en" and not is_credentials_message:
            devanagari_chars = sum(1 for c in reply_text if "\u0900" <= c <= "\u097f")
            if devanagari_chars < len(reply_text) * 0.3:
                original_reply = reply_text
                try:
                    from ai_sahayak.language.translation.pipeline import TranslationPipeline
                    translator = TranslationPipeline()
                    reply_text = await translator.translate_from_english(reply_text, "hi")
                    if not (reply_text and reply_text.strip()):
                        reply_text = original_reply
                except Exception as tr_err:
                    print(f"[Chat] Translation to Hindi failed: {tr_err}")
                    reply_text = original_reply
        
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
