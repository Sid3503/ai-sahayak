from datetime import datetime
import pytz

class CulturalFormatter:
    INDIA_TIMEZONE = pytz.timezone("Asia/Kolkata")
    
    def format_date(self, date_obj: datetime, lang: str) -> str:
        """Format dates according to regional preferences"""
        if lang in ["hi", "mr", "bn"]:
            # Indian English format with regional calendar context
            return f"{date_obj.strftime('%d-%m-%Y')} ({self._get_indian_festival(date_obj)})"
        return date_obj.strftime("%Y-%m-%d")
        
    def format_currency(self, amount: float, lang: str) -> str:
        """Format currency with regional symbols"""
        formats = {
            "en": f"₹{amount:,.2f}",
            "hi": f"₹{amount:,.2f} रुपए",
            "mr": f"₹{amount:,.2f} रुपये", 
            "bn": f"₹{amount:,.2f} টাকা"
        }
        return formats.get(lang, f"₹{amount:,.2f}")
        
    def _get_indian_festival(self, date_obj: datetime) -> str:
        """Map dates to upcoming Indian festivals"""
        festivals = {
            (1, 14): "Makar Sankranti",
            (3, 8): "Holi",
            (4, 14): "Baisakhi",
            (8, 15): "Independence Day",
            (10, 2): "Gandhi Jayanti",
            (10, 24): "Diwali"
        }
        return festivals.get((date_obj.month, date_obj.day), "")
