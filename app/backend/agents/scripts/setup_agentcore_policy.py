import boto3
import os
from ai_sahayak.config.settings import settings

def setup_agentcore_policies():
    """
    Sets up natural language guardrails for AI Sahayak using Bedrock AgentCore.
    """
    client = boto3.client("bedrock-agent", region_name=settings.BEDROCK_REGION)
    
    print("🚀 Setting up AI Sahayak Safety Policies in AgentCore...")
    
    try:
        # Note: In a real AWS environment, this would create an actual Policy resource.
        # This mirrors the proposed Service 6 implementation.
        response = client.create_agent_core_policy(
            name="ai-sahayak-safety-policy",
            policies=[
                "The agent can only query DynamoDB records where store_id matches the actor_id from the current session.",
                "The pricing agent can read competitor prices but cannot modify any price records.",
                "The whatif simulator can perform calculations but cannot place real orders or modify inventory.",
                "The agent must always respond in the user's detected preferred language."
            ]
        )
        print(f"✅ Policy created: {response.get('agentCorePolicyId')}")
    except Exception as e:
        print(f"⚠️ AgentCore Policy Setup (Simulation/Mock): {e}")
        print("Continuing with local safety logic fallback...")

if __name__ == "__main__":
    setup_agentcore_policies()
