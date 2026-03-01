import boto3
import os

dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION", "ap-south-1"))
table = dynamodb.Table("ai_sahayak_conversation_history")

response = table.scan()
items = response.get('Items', [])
print(f"Total items in ai_sahayak_conversation_history: {len(items)}")
if items:
    print(f"Sample session_id: {items[0].get('session_id')}")
    print(f"Message count in sample: {len(items[0].get('messages', []))}")
