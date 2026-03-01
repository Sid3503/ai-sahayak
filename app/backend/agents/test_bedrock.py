import boto3
import os

client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "ap-south-1"))

try:
    response = client.converse(
        modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        messages=[{"role": "user", "content": [{"text": "Hello"}]}]
    )
    print("Success with us.anthropic.claude-3-5-haiku-20241022-v1:0")
except Exception as e:
    print(f"Error 1: {e}")

try:
    response = client.converse(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=[{"role": "user", "content": [{"text": "Hello"}]}]
    )
    print("Success with us.anthropic.claude-haiku-4-5-20251001-v1:0")
except Exception as e:
    print(f"Error 2: {e}")
