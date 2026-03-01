import os
from dotenv import load_dotenv, set_key
from bedrock_agentcore.memory.controlplane import MemoryControlPlaneClient

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(env_path)

def setup_memory():
    region = os.getenv("AWS_REGION", "ap-south-1")
    print(f"Initializing Bedrock AgentCore Memory in {region}...")
    
    client = MemoryControlPlaneClient(region_name=region)
    
    # Check if we already have it
    current_memory_id = os.getenv("AGENTCORE_MEMORY_ID")
    if current_memory_id and current_memory_id != "lauki_agent_memory-Yrm3JrG0Vz" and current_memory_id != "default_memory_id-12345abcde":
        try:
            print(f"Checking existing memory: {current_memory_id}")
            memory = client.get_memory(current_memory_id)
            print(f"✅ Memory already exists: {current_memory_id}")
            return
        except Exception:
            print(f"Existing memory ID invalid or not found. Creating a new one.")

    # Create Memory
    print("Creating new Memory...")
    response = client.create_memory(
        name="ai_sahayak_memory",
        event_expiry_days=90,
        description="Memory for AI Sahayak users",
        wait_for_active=True
    )
    
    memory_id = response["id"]
    print(f"✅ Successfully created Bedrock Memory. ID: {memory_id}")
    
    # Save to .env
    set_key(env_path, "AGENTCORE_MEMORY_ID", memory_id)
    print(f"✅ .env file updated with AGENTCORE_MEMORY_ID=\"{memory_id}\"")

if __name__ == "__main__":
    setup_memory()
