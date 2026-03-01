import uvicorn
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from ai_sahayak.api.server import create_app

# Wire AgentCore Observability via OpenTelemetry
# Fallback to ConsoleSpanExporter for local debugging since vendor-specific exporter was not found
# provider = TracerProvider()
# provider.add_span_processor(
#     BatchSpanProcessor(ConsoleSpanExporter())
# )
# trace.set_tracer_provider(provider)

fastapi_app = create_app()

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
