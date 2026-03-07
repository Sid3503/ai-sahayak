"""
Run this ONCE to create the EventBridge rule that triggers the festival orchestrator Lambda
for ALL retailers (raju, ramesh, suresh, kanta, lakshmi) in one invocation, daily.

Usage:
  python setup_eventbridge_orchestrator.py --lambda-arn <orchestrator-lambda-arn> --region ap-south-1

The rule sends payload: {"run_all_retailers": true}
Lambda then runs run_daily_orchestration for each dataset_key and posts alerts per user_id to the backend.
"""
import argparse
import json
import boto3

RULE_NAME = "ai-sahayak-festival-orchestrator-daily"
SCHEDULE = "cron(0 0 * * ? *)"  # 0:00 UTC = 5:30 AM IST every day; change as needed
DESCRIPTION = "Triggers festival orchestrator for all 5 retailers (raju, ramesh, suresh, kanta, lakshmi) daily"
# Payload so Lambda runs for all users in one go
TARGET_INPUT = json.dumps({"run_all_retailers": True})


def setup_rule(lambda_arn: str, region: str):
    events = boto3.client("events", region_name=region)
    lam = boto3.client("lambda", region_name=region)

    print(f"Creating EventBridge rule: {RULE_NAME}")
    rule_resp = events.put_rule(
        Name=RULE_NAME,
        ScheduleExpression=SCHEDULE,
        State="ENABLED",
        Description=DESCRIPTION,
    )
    rule_arn = rule_resp["RuleArn"]
    print(f"Rule ARN: {rule_arn}")

    print("Adding Lambda as target with payload: run_all_retailers=true")
    events.put_targets(
        Rule=RULE_NAME,
        Targets=[
            {
                "Id": "FestivalOrchestratorLambda",
                "Arn": lambda_arn,
                "Input": TARGET_INPUT,
            }
        ],
    )

    print("Adding permission for EventBridge to invoke Lambda...")
    try:
        lam.add_permission(
            FunctionName=lambda_arn,
            StatementId="allow-eventbridge-orchestrator-daily",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn,
        )
        print("Permission added.")
    except lam.exceptions.ResourceConflictException:
        print("Permission already exists - skipping.")

    print(f"\nDone! EventBridge rule '{RULE_NAME}' will trigger the orchestrator daily for all retailers.")
    print(f"Schedule: {SCHEDULE} (adjust in script if you want different time)")
    print(f"Lambda: {lambda_arn}")
    print("Payload: run_all_retailers=true -> raju, ramesh, suresh, kanta, lakshmi each get their forecast and Live Alert.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lambda-arn", required=True, help="ARN of the ai-sahayak-festival-orchestrator Lambda")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1)")
    args = parser.parse_args()
    setup_rule(args.lambda_arn, args.region)
