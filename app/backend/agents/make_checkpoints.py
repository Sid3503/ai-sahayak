import boto3
import os
import time
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb', region_name=os.getenv("AWS_REGION", "ap-south-1"))

try:
    dynamodb.delete_table(TableName='ai_sahayak_checkpoints')
    print("Deleted old table")
except ClientError:
    pass

time.sleep(5)

try:
    dynamodb.create_table(
        TableName='ai_sahayak_checkpoints',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Created ai_sahayak_checkpoints with PK and SK")
except ClientError as e:
    print(e)
