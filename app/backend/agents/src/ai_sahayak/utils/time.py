from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_now_ist() -> datetime:
    return datetime.now(IST)

def format_date_for_user(dt: datetime, locale: str = "hi") -> str:
    # Formatting logic based on locale
    return dt.strftime("%d %b %Y")
