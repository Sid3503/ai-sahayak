import uuid
from typing import List, Optional
from datetime import datetime
from ai_sahayak.schemas.alerts import ProactiveAlert, AlertCategory, AlertSeverity
from ai_sahayak.tools.data_sources.dynamodb_tool import DynamoDBTool

class AlertManager:
    """Manages creation, retrieval, and dispatch of proactive alerts for users."""
    
    def __init__(self):
        self.db_tool = MongoDBTool()
        
    async def create_alert(self, store_id: str, category: AlertCategory, severity: AlertSeverity, title: str, message: str, actions: List[str] = None) -> ProactiveAlert:
        """Create and store a new alert."""
        alert = ProactiveAlert(
            alert_id=f"alrt_{uuid.uuid4().hex[:8]}",
            store_id=store_id,
            category=category,
            severity=severity,
            title=title,
            message=message,
            suggested_actions=actions or [],
            timestamp=datetime.utcnow()
        )
        
        # In a full implementation, you'd store this in self.db_tool.db.alerts
        await self.db_tool.db.alerts.insert_one(alert.model_dump())
        return alert
        
    async def get_active_alerts(self, store_id: str, limit: int = 5) -> List[ProactiveAlert]:
        """Fetch active alerts for a given store."""
        raw_alerts = await self.db_tool.db.alerts.find({"store_id": store_id}).sort("timestamp", -1).limit(limit).to_list(length=limit)
        return [ProactiveAlert(**a) for a in raw_alerts]

    async def generate_mock_festival_alert(self, store_id: str) -> ProactiveAlert:
        """Generates a seasonal alert for demonstration."""
        return await self.create_alert(
            store_id=store_id,
            category=AlertCategory.SEASONAL,
            severity=AlertSeverity.INFO,
            title="Holi Festival Upcoming!",
            message="Holi is in 2 weeks. Based on last year's trends, you should stock up on Gulaal and Gujiya ingredients. Prices might spike next week.",
            actions=["📦 Update Inventory", "💰 Check Wholesale Price"]
        )
