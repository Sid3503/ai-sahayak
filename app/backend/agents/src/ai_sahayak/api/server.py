from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_sahayak.api.routes import health, chat, webhook_whatsapp, calendar, tts, alerts, profile

def create_app() -> FastAPI:
    app = FastAPI(title="AI Sahayak Agents API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/health", tags=["System"])
    app.include_router(chat.router, prefix="/v1", tags=["Chat"])
    app.include_router(webhook_whatsapp.router, prefix="/v1/webhooks", tags=["Webhooks"])
    app.include_router(calendar.router, prefix="/v1", tags=["Calendar"])
    app.include_router(tts.router, prefix="/v1", tags=["TTS"])
    app.include_router(alerts.router, prefix="/v1", tags=["Alerts"])
    app.include_router(profile.router, prefix="/v1", tags=["Profile"])

    return app
