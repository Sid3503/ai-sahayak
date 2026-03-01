import boto3
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("APP_ENV", "dev")

if ENV == "dev":
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="ap-south-1",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="fake",
        aws_secret_access_key="fake"
    )
else:
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "ap-south-1")
    )

def table_exists(name: str) -> bool:
    try:
        dynamodb.Table(name).load()
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return False

# 1. User Info (formerly ai_sahayak.user_info)
def create_user_info_table():
    name = "ai_sahayak_user_info"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "phone_number", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "phone-index",
                "KeySchema": [
                    {"AttributeName": "phone_number", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Created: {name}")

# 2. Conversation History (formerly ai_sahayak.conversation_history)
def create_conversation_history_table():
    name = "ai_sahayak_conversation_history"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "session_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "session_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Created: {name}")

# 3. Stores (formerly ai_sahayak.stores)
def create_stores_table():
    name = "ai_sahayak_stores"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "store_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "store_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Created: {name}")

# 4. Inventory (formerly ai_sahayak.inventory)
def create_inventory_table():
    name = "ai_sahayak_inventory"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "sku_id", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "sku_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Created: {name}")

# 5. Sales (formerly ai_sahayak.sales)
def create_sales_table():
    name = "ai_sahayak_sales"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Created: {name}")

# 6. Audit Logs (formerly ai_sahayak.audit_logs)
def create_audit_logs_table():
    name = "ai_sahayak_audit_logs"
    if table_exists(name):
        print(f"✅ {name} already exists — skipping")
        return

    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "log_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "log_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    sys_ttl = dynamodb.meta.client.update_time_to_live(
        TableName=name,
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': 'ttl' # Equivalent to expireAfterSeconds 7776000
        }
    )
    print(f"✅ Created: {name}")



if __name__ == "__main__":
    print(f"\\n🚀 Setting up DynamoDB tables [{ENV}]\\n")
    create_user_info_table()
    create_conversation_history_table()
    create_stores_table()
    create_inventory_table()
    create_sales_table()
    create_audit_logs_table()
    print("\\n✅ All tables ready!\\n")
