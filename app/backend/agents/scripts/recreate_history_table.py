import boto3
import os
import time
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.client('dynamodb', region_name=os.getenv("AWS_REGION", "ap-south-1"))

table_name = "ai_sahayak_conversation_history"
try:
    print(f"Deleting table {table_name}...")
    dynamodb.delete_table(TableName=table_name)
    waiter = dynamodb.get_waiter('table_not_exists')
    waiter.wait(TableName=table_name)
    print("Table deleted.")
except dynamodb.exceptions.ResourceNotFoundException:
    print("Table didn't exist.")

import setup_dynamodb
print("Recreating table with new schema...")
setup_dynamodb.create_conversation_history_table()
