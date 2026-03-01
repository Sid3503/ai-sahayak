import boto3
import os
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION", "ap-south-1"))

tables_to_clear = [
    "ai_sahayak_user_info",
    "ai_sahayak_conversation_history",
    "ai_sahayak_stores",
    "ai_sahayak_inventory",
    "ai_sahayak_sales",
    "ai_sahayak_audit_logs"
]

def clear_table(table_name):
    print(f"Scanning and deleting items from {table_name}...")
    table = dynamodb.Table(table_name)
    try:
        # Get primary key names
        keys = [k['AttributeName'] for k in table.key_schema]
        
        scan = table.scan()
        with table.batch_writer() as batch:
            for each in scan.get('Items', []):
                key_dict = {k: each[k] for k in keys}
                batch.delete_item(Key=key_dict)
                
        # Handle pagination if table is large
        while 'LastEvaluatedKey' in scan:
            scan = table.scan(ExclusiveStartKey=scan['LastEvaluatedKey'])
            with table.batch_writer() as batch:
                for each in scan.get('Items', []):
                    key_dict = {k: each[k] for k in keys}
                    batch.delete_item(Key=key_dict)
                    
        print(f"✅ Cleared all items from {table_name}")
    except Exception as e:
        print(f"⚠️ Could not clear {table_name}: {e}")

if __name__ == "__main__":
    print("🧹 Wiping all DynamoDB tables...\n")
    for t in tables_to_clear:
        clear_table(t)
    print("\n✅ Database is now completely empty.")
