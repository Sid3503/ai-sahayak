import os
from langgraph_checkpoint_aws import DynamoDBSaver

# Standard DynamoDB Checkpointer for LangGraph - short-term thread state
checkpointer = DynamoDBSaver(
    table_name="ai_sahayak_checkpoints",
    region_name=os.getenv("AWS_REGION", "ap-south-1")
)
