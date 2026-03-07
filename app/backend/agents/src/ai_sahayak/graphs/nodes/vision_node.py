from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.vision.shelf_analyzer import ShelfAnalyzer
import os

async def image_analysis_node(state: ConversationState):
    """
    Handles image analysis requests (e.g., Shelf Eye).
    """
    image_path = state.get("image_path")

    if not image_path or not os.path.exists(image_path):
        return {
            "messages": [AIMessage(content="I couldn't access the image you uploaded. Please try again.")],
            "current_step": "image_analysis_failed"
        }

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        import base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        analyzer = ShelfAnalyzer()
        analysis_result = await analyzer.analyze_shelf_image(base64_image=base64_image)

        status = analysis_result.get("status")
        if status == "success":
            insights = analysis_result.get("insights", {})
            stock_level = insights.get("overall_stock_level", "Unknown")
            updates = analysis_result.get("inventory_updates", [])

            message = f"📸 **Shelf Eye Analysis Complete**\n\nOverall Stock Level: **{stock_level}**\n\nI noticed the following details:\n"
            for update in updates[:3]:
                message += f"- {update.get('product', 'Item')}: {update.get('status', 'Unknown')} (Est. {update.get('estimated_count', 'N/A')})\n"

            if len(updates) > 3:
                message += f"\nAnd {len(updates) - 3} more items updated in your inventory."

            return {
                "messages": [AIMessage(content=message)],
                "current_step": "image_analysis_complete",
                "vision_analysis": analysis_result
            }
        else:
            return {
                "messages": [AIMessage(content="I analyzed the image but couldn't extract clear inventory insights right now.")],
                "current_step": "image_analysis_partial"
            }

    except Exception as e:
        print(f"Vision node error: {e}")
        return {
            "messages": [AIMessage(content="Sorry, I ran into an error while analyzing your image.")],
            "current_step": "image_analysis_error"
        }
