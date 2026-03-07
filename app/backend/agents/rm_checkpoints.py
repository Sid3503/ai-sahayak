import boto3
import os

dynamodb = boto3.client('dynamodb', region_name=os.getenv("AWS_REGION", "ap-south-1"))

try:
    dynamodb.delete_table(TableName='ai_sahayak_checkpoints')
    print("✅ Deleted ai_sahayak_checkpoints table")
except Exception as e:
    print(f"Error: {e}")
