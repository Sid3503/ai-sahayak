"""
DynamoDB tool for user and store profiles. Used by onboarding and load_profile.
"""
import os
import boto3
from ai_sahayak.config.settings import settings

_ENV = getattr(settings, "APP_ENV", "dev")
_REGION = getattr(settings, "AWS_REGION", "ap-south-1")


def _get_resource():
    if _ENV == "dev" and os.getenv("DYNAMODB_ENDPOINT_URL"):
        return boto3.resource(
            "dynamodb",
            region_name=_REGION,
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"),
        )
    return boto3.resource("dynamodb", region_name=_REGION)


class DynamoDBTool:
    def __init__(self):
        self.dynamodb = _get_resource()
        self.user_table = self.dynamodb.Table(settings.USERS_TABLE)
        self.store_table = self.dynamodb.Table(getattr(settings, "STORES_TABLE", "ai-sahayak-stores"))

    async def get_store_profile(self, store_id: str):
        """Get store profile by store_id (e.g. store_<user_id>)."""
        try:
            response = self.store_table.get_item(Key={"store_id": store_id})
            return response.get("Item")
        except Exception as e:
            print(f"[DynamoDBTool] get_store_profile failed: {e}")
            return None

    async def get_user_profile(self, user_id: str):
        """Get user profile by user_id (same as Cognito username / phone). Returns { name, ... } or None."""
        try:
            response = self.user_table.get_item(Key={"user_id": user_id})
            return response.get("Item")
        except Exception as e:
            print(f"[DynamoDBTool] get_user_profile failed: {e}")
            return None

    async def upsert_user_profile(
        self,
        user_id: str,
        name: str,
        phone: str = None,
        password: str = None,
    ):
        """Insert or update user profile. Uses USERS_TABLE with key user_id."""
        try:
            update_expr = "SET #n = :n"
            expr_attrs = {":n": name}
            expr_names = {"#n": "name"}
            if phone is not None:
                update_expr += ", phone_number = :p"
                expr_attrs[":p"] = str(phone)[:20]
            if password is not None:
                update_expr += ", #pwd = :pwd"
                expr_attrs[":pwd"] = str(password)[:64]
                expr_names["#pwd"] = "password"
            self.user_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attrs,
                ExpressionAttributeNames=expr_names,
                ReturnValues="UPDATED_NEW",
            )
        except Exception as e:
            print(f"[DynamoDBTool] upsert_user_profile failed: {e}")

    async def upsert_store_profile(self, user_id: str, store_name: str, location: str):
        """Insert or update store profile. store_id = store_<user_id>."""
        try:
            store_id = f"store_{user_id}"
            self.store_table.update_item(
                Key={"store_id": store_id},
                UpdateExpression="SET owner_id = :o, #n = :n, #l = :l",
                ExpressionAttributeValues={
                    ":o": user_id,
                    ":n": store_name,
                    ":l": location,
                },
                ExpressionAttributeNames={"#n": "name", "#l": "location"},
                ReturnValues="UPDATED_NEW",
            )
        except Exception as e:
            print(f"[DynamoDBTool] upsert_store_profile failed: {e}")
