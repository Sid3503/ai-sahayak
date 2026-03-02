import os
import boto3
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("APP_ENV", "dev")

def _get_resource():
    if ENV == "dev":
        return boto3.resource(
            "dynamodb",
            region_name="ap-south-1",
            endpoint_url="http://localhost:8000",
            aws_access_key_id="fake",
            aws_secret_access_key="fake"
        )
    return boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "ap-south-1"))

class DynamoDBTool:
    def __init__(self):
        self.dynamodb = _get_resource()
        self.sales_table = self.dynamodb.Table("ai_sahayak_sales")
        self.inventory_table = self.dynamodb.Table("ai_sahayak_inventory")
        self.store_table = self.dynamodb.Table("ai_sahayak_stores")
        self.user_table = self.dynamodb.Table("ai_sahayak_user_info")

    async def get_store_profile(self, store_id: str):
        response = self.store_table.get_item(Key={"store_id": store_id})
        return response.get("Item")

    async def upsert_user_profile(self, user_id: str, name: str, phone: str = None, password: str = None):
        """Optimally insert or update a user profile."""
        update_expr = "set #n = :n"
        expr_attrs = {":n": name}
        expr_names = {"#n": "name"}
        
        if phone:
            update_expr += ", phone_number = :p"
            expr_attrs[":p"] = phone
            
        if password:
            update_expr += ", password = :pwd"
            expr_attrs[":pwd"] = password
            
        self.user_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attrs,
            ExpressionAttributeNames=expr_names,
            ReturnValues="UPDATED_NEW"
        )

    async def upsert_store_profile(self, user_id: str, store_name: str, location: str, pincode: str | None = None):
        """Optimally insert or update a store profile, linking to the user."""
        store_id = f"store_{user_id}"

        update_expr = "set owner_id = :o, #n = :n, #l = :l"
        expr_values: dict = {":o": user_id, ":n": store_name, ":l": location}
        expr_names: dict = {"#n": "name", "#l": "location"}

        if pincode:
            update_expr += ", pincode = :pc"
            expr_values[":pc"] = pincode

        self.store_table.update_item(
            Key={"store_id": store_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names,
            ReturnValues="UPDATED_NEW",
        )
