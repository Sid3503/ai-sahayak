import boto3
import os
from ai_sahayak.config.settings import settings


class AgentCoreGatewayClient:
    """
    Client for interacting with Bedrock AgentCore Gateway.
    Centralizes tool discovery and execution.
    """
    def __init__(self):
        self.client = boto3.client("bedrock-agent-runtime", region_name=settings.BEDROCK_REGION)
        self.gateway_endpoint = os.getenv("AGENTCORE_GATEWAY_ENDPOINT") or settings.AGENTCORE_GATEWAY_ENDPOINT or ""

    async def invoke_tool(self, tool_name: str, input_data: dict) -> dict:
        """
        Invokes a tool via the AgentCore Gateway.
        """
        if not self.gateway_endpoint:
            # Fallback to direct tool execution if Gateway is not configured
            print(f"[Gateway] Offline: Falling back to direct execution for {tool_name}")
            return await self._local_fallback(tool_name, input_data)

        try:
            response = self.client.invoke_agent_core_gateway_target(
                agentCoreGatewayEndpoint=self.gateway_endpoint,
                toolName=tool_name,
                inputData=input_data
            )
            return response["output"]
        except Exception as e:
            print(f"[Gateway] Error: {e}. Falling back...")
            return await self._local_fallback(tool_name, input_data)

    async def _local_fallback(self, tool_name: str, input_data: dict) -> dict:
        # No mock data — all data must come from Dashboard only
        return {"status": "error", "message": "Data only from Dashboard. Control Centre connect karein, phir try karein."}


gateway_client = AgentCoreGatewayClient()
