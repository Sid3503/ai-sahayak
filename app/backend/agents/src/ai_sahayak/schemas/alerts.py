from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertCategory(str, Enum):
    INVENTORY = "INVENTORY"
    PRICING = "PRICING"
    SEASONAL = "SEASONAL"
    SALES = "SALES"

class ProactiveAlert(BaseModel):
    """Schema for a proactive generated alert."""
    alert_id: str
    store_id: str
    category: AlertCategory
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suggested_actions: List[str] = []
    metadata: Dict[str, Any] = {}

class WhatIfScenarioRequest(BaseModel):
    """Schema for a what-if simulation request."""
    store_id: str
    target_metric: str # e.g., "revenue", "profit", "footfall"
    scenario_description: str # e.g., "What if I drop Maggi price by 10%?"
    
class WhatIfScenarioResult(BaseModel):
    """Schema for a what-if simulation result."""
    scenario_id: str
    predicted_impact: str # e.g., "Positive", "Negative", "Neutral"
    estimated_metric_change: float # e.g., 5.0 (+5%)
    explanation_text: str
    confidence_score: float # 0.0 to 1.0
