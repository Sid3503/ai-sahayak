"""
Run this ONCE to create the EventBridge rule that triggers alerts_handler Lambda
daily at 9:00 AM IST (3:30 AM UTC) using a cron schedule.

Usage:
  python setup_eventbridge_rule.py --lambda-arn <your-lambda-arn> --region ap-south-1
"""
import argparse
import json
import boto3

RULE_NAME = "ai-sahayak-festival-alerts-daily"
SCHEDULE = "cron(30 3 * * ? *)"  # 3:30 AM UTC = 9:00 AM IST every day
DESCRIPTION = "Triggers AI Sahayak festival alert Lambda daily at 9 AM IST for Raju Bhai"


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

    print("Adding Lambda as target...")
    events.put_targets(
        Rule=RULE_NAME,
        Targets=[{
            "Id": "FestivalAlertsLambda",
            "Arn": lambda_arn,
        }],
    )

    print("Adding permission for EventBridge to invoke Lambda...")
    try:
        lam.add_permission(
            FunctionName=lambda_arn,
            StatementId="allow-eventbridge-festival-alerts",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn,
        )
        print("Permission added.")
    except lam.exceptions.ResourceConflictException:
        print("Permission already exists - skipping.")

    print(f"\nDone! EventBridge rule '{RULE_NAME}' will trigger your Lambda daily at 9 AM IST.")
    print(f"Schedule: {SCHEDULE}")
    print(f"Lambda: {lambda_arn}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lambda-arn", required=True, help="ARN of the alerts_handler Lambda function")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1)")
    args = parser.parse_args()
    setup_rule(args.lambda_arn, args.region)
