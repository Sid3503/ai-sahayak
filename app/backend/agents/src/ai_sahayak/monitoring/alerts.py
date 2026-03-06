import uuid
from typing import List, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from ai_sahayak.schemas.alerts import ProactiveAlert, AlertCategory, AlertSeverity
from ai_sahayak.config.settings import settings

_dynamo_table = None


def _get_alerts_table():
    global _dynamo_table
    if not settings.ALERTS_TABLE:
        return None
    if _dynamo_table is None:
        _dynamo_table = boto3.resource("dynamodb", region_name=settings.AWS_REGION).Table(settings.ALERTS_TABLE)
    return _dynamo_table


class AlertManager:
    """
    Manages creation, retrieval, and dispatch of proactive alerts for users.
    Persists to DynamoDB when ALERTS_TABLE is set; otherwise in-memory only.
    """
    def __init__(self):
        pass

    async def create_alert(
        self,
        store_id: str,
        category: AlertCategory,
        severity: AlertSeverity,
        title: str,
        message: str,
        actions: Optional[List[str]] = None,
    ) -> ProactiveAlert:
        """Create and return a new alert; persist to DynamoDB when ALERTS_TABLE is set."""
        alert = ProactiveAlert(
            alert_id=f"alrt_{uuid.uuid4().hex[:8]}",
            store_id=store_id,
            category=category,
            severity=severity,
            title=title,
            message=message,
            suggested_actions=actions or [],
            timestamp=datetime.utcnow(),
        )
        table = _get_alerts_table()
        if table:
            try:
                table.put_item(Item={
                    "alert_id": alert.alert_id,
                    "store_id": alert.store_id,
                    "category": alert.category.value,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "suggested_actions": alert.suggested_actions,
                    "timestamp": alert.timestamp.isoformat(),
                })
            except ClientError as e:
                print(f"[AlertManager] DynamoDB put_item failed: {e}")
        return alert

    async def get_active_alerts(self, store_id: str, limit: int = 5) -> List[ProactiveAlert]:
        """Fetch active alerts for a given store from DynamoDB when ALERTS_TABLE is set."""
        table = _get_alerts_table()
        if not table:
            return []
        try:
            resp = table.query(
                KeyConditionExpression="store_id = :sid",
                ExpressionAttributeValues={":sid": store_id},
                Limit=limit,
                ScanIndexForward=False,
            )
            items = resp.get("Items", [])
            return [
                ProactiveAlert(
                    alert_id=it["alert_id"],
                    store_id=it["store_id"],
                    category=AlertCategory(it["category"]),
                    severity=AlertSeverity(it["severity"]),
                    title=it["title"],
                    message=it["message"],
                    suggested_actions=it.get("suggested_actions", []),
                    timestamp=datetime.fromisoformat(it["timestamp"]) if isinstance(it.get("timestamp"), str) else it.get("timestamp"),
                )
                for it in items
            ]
        except ClientError as e:
            print(f"[AlertManager] DynamoDB query failed: {e}")
            return []

    async def generate_mock_festival_alert(self, store_id: str) -> ProactiveAlert:
        """Generates a seasonal alert for demonstration."""
        return await self.create_alert(
            store_id=store_id,
            category=AlertCategory.SEASONAL,
            severity=AlertSeverity.INFO,
            title="Holi Festival Upcoming!",
            message="Holi is in 2 weeks. Based on last year's trends, you should stock up on Gulaal and Gujiya ingredients. Prices might spike next week.",
            actions=["📦 Update Inventory", "💰 Check Wholesale Price"],
        )
