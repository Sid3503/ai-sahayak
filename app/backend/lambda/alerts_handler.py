"""
Lambda: AI Sahayak — Daily Alert Handler
- Runs daily via EventBridge (default 9 AM IST, but per-user time preference supported)
- For each registered user, fetches their preferences from DynamoDB:
    * user_id — must be retailer key (raju, ramesh, suresh, kanta, lakshmi) so Live Alerts / My day UI shows that user's alerts
    * alert_days_before  — how many days ahead to alert (user-configurable, default 5)
    * alert_time_hour_ist — what hour (0-23 IST) they want alerts; only at that hour (default 9)
- Merges national calendar + state-specific regional calendar from S3 (ai-sahayak-calendar bucket)
- Fetches Kirana/FMCG-relevant news from RSS (not stock market, small seller focus)
- Posts Hinglish alerts to the AI Sahayak backend webhook (POST /v1/alerts/incoming)
"""

import json
import os
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError

# ── Global defaults (overridden per user from DynamoDB) ─────────────────────
DEFAULT_ALERT_DAYS     = int(os.environ.get("ALERT_DAYS_BEFORE", "5"))
DEFAULT_ALERT_HOUR_IST = int(os.environ.get("ALERT_TIME_HOUR_IST", "9"))  # 9 AM IST if user hasn't set
CALENDAR_S3_BUCKET   = os.environ.get("CALENDAR_S3_BUCKET", "")
NATIONAL_S3_KEY      = os.environ.get("NATIONAL_S3_KEY", "panchang/national.json")
REGIONAL_S3_PREFIX   = os.environ.get("REGIONAL_S3_PREFIX", "panchang/regional_")
USERS_TABLE          = os.environ.get("USERS_TABLE", "ai-sahayak-users")
BACKEND_WEBHOOK_URL  = os.environ.get("BACKEND_WEBHOOK_URL", "")
# Optional: Systems Manager Change Calendar = "digital Panchang". When set, Lambda only runs when calendar state is OPEN.
SSM_CALENDAR_NAME    = os.environ.get("SSM_CALENDAR_NAME", "")  # e.g. "ai-sahayak-panchang"

# Kirana/FMCG-focused RSS feeds — small seller relevant news only
NEWS_RSS_URLS = [
    # FMCG & retail price news
    "https://www.thehindubusinessline.com/economy/agri-business/?service=rss",
    # Govt schemes, GST, tax for small biz
    "https://economictimes.indiatimes.com/small-biz/rssfeeds/18322036.cms",
    # Commodity prices (edible oil, sugar, wheat etc.)
    "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/1808152121.cms",
    # Fallback: general ET
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]

# Keywords that make news RELEVANT to Raju (Kirana owner)
RELEVANT_KEYWORDS = [
    "fmcg", "kirana", "retail", "grocery", "price hike", "price rise", "price cut",
    "inflation", "gst", "tax", "wholesale", "edible oil", "sugar", "wheat", "flour",
    "dal", "pulses", "rice", "onion", "potato", "tomato", "upi", "payment",
    "small business", "msme", "trader", "shopkeeper", "commodity", "import duty",
    "export ban", "subsidy", "ration", "food", "beverage", "snack", "biscuit",
    "soap", "detergent", "shampoo", "packaging", "supply chain", "shortage",
    "festival", "demand", "stock", "inventory", "distribution",
]

STATE_CODE_MAP = {
    "MP": "mp",  "MH": "mh",  "GJ": "gj",  "WB": "wb",
    "TN": "tn",  "AP": "ap_ts", "TS": "ap_ts",
    "RJ": "rj",  "PB": "pb_hr", "HR": "pb_hr",
    "UP": "up_uk", "UK": "up_uk",
    "BR": "br_jh", "JH": "br_jh",
    "KA": "ka",  "KL": "kl",
    "DL": "dl",  "OD": "od",
    "AS": "as_ne", "MN": "as_ne", "ML": "as_ne", "NL": "as_ne",
    "TR": "as_ne", "AR": "as_ne", "SK": "as_ne", "MZ": "as_ne",
    "CG": "cg",  "HP": "hp_jk", "JK": "hp_jk", "LA": "hp_jk",
}

FESTIVAL_MESSAGES = {
    "holi":                 "Raju Bhai, Holi aa rahi hai! Gulal, Pichkari, Ghee aur Shakkar ka stock check karo!",
    "holika dahan":         "Kal Holika Dahan hai! Naariyal aur Pooja items ka stock ready rakho.",
    "diwali":               "Diwali aane wali hai! Mithai, Dry fruits, Diyas, Candles aur Gift packs ka stock prepare karo. Ye season miss mat karo!",
    "chaitra navratri":     "Navratri shuru hone wali hai! Sabudana, Singhara atta, Kuttu aur Fruits ka stock badha lo.",
    "navratri (sharad)":    "Sharad Navratri aa rahi hai! Farali items, Sabudana, Kuttu, Dahi ka stock check karo.",
    "raksha bandhan":       "Raksha Bandhan aane wala hai! Rakhi, Mithai, Chocolates aur Gift boxes ready rakho.",
    "janmashtami":          "Janmashtami aa rahi hai! Makhan, Mishri, Dahi, Panjiri aur Prasad items ka stock rakho.",
    "ganesh chaturthi":     "Ganesh Chaturthi aane wali hai! Modak, Coconut, Flowers aur Incense ka stock check karo.",
    "dussehra":             "Dussehra aane wala hai! Sweets, Jalebi, Samosa aur FMCG ka stock prepare karo.",
    "chhath puja":          "Chhath Puja aane wali hai! Thekua, Gur, Sugarcane, Fruits aur Bamboo soop ka stock rakh lo.",
    "guru nanak jayanti":   "Guru Nanak Jayanti aa rahi hai! Langar items — Atta, Ghee, Dal aur Sugar ka stock check karo.",
    "eid ul-fitr":          "Eid ul-Fitr aane wali hai! Sewai, Dates, Dry fruits, Ittar aur Gift packs ka stock prepare karo.",
    "eid ul-adha":          "Eid ul-Adha aa raha hai! Dry fruits, Sewai, Spices aur Gift packs ka stock check karo.",
    "christmas":            "Christmas aane wala hai! Cakes, Chocolates, Candles aur Gift packs ka stock ready rakho.",
    "new year eve":         "New Year aa raha hai! Cold drinks, Chips, Party snacks ka stock check karo.",
    "makar sankranti":      "Makar Sankranti aa rahi hai! Til, Gur, Peanuts aur Kite string ka stock ready rakho.",
    "akshaya tritiya":      "Akshaya Tritiya aa rahi hai! Sweets, Dry fruits aur Gift boxes ki demand badh sakti hai.",
    "independence day":     "Independence Day aa raha hai! Tricolor items, Flags aur Sweets ready rakho.",
    "republic day":         "Republic Day aa raha hai! Tricolor flags, Sweets aur Cold drinks ka stock ready rakho.",
    "maha shivratri":       "Maha Shivratri aane wali hai! Milk, Bel patra, Bhang aur Dry fruits ka stock check karo.",
    "onam":                 "Onam aa raha hai! Rice, Banana chips, Coconut oil aur Payasam ingredients ka stock rakho.",
    "pongal":               "Pongal aane wala hai! Rice, Jaggery, Sugarcane aur Pooja items ka stock prepare karo.",
    "ugadi":                "Ugadi aa rahi hai (Naya Saal)! Sweets, Raw mango, Neem flowers ki demand badh sakti hai.",
    "durga puja":           "Durga Puja aane wali hai! New clothes, Sweets, Flowers aur Puja items ka stock check karo.",
    "lohri":                "Lohri aa rahi hai! Rewri, Gajak, Peanuts, Popcorn aur Til ka stock check karo.",
    "baisakhi":             "Baisakhi aa rahi hai! New clothes, Mustard items aur Lassi ingredients ki demand rahegi.",
    "rangpanchami":         "Rangpanchami aane wali hai! Gulal, Rang aur Pichkari ka stock check karo — Indore mein ye Holi se bada hai!",
    "wedding season":       "Shaadi ka season aa raha hai! Dry fruits, Mithai, Gift packs ki demand badh sakti hai.",
    "school reopening":     "School reopen hone wala hai! Stationery, Notebooks, Snacks aur Daily-use items ka stock check karo.",
    "diwali shopping rush": "Diwali shopping rush shuru hone wala hai! Gift packs, Dry fruits, Mithai aur Sweets ready rakho.",
    "dhanteras":            "Dhanteras aa raha hai! Brooms, Diyas, Utensils aur Sweets ka stock ready rakho — ek din mein sabse zyada bikri!",
}

GENERIC_MESSAGE = "Raju Bhai, {name} aane wali hai! Stock check kar lijiye aur preparation shuru kar do."


def event_confidence_score(days_until_event: int, event_type: str = "festival") -> int:
    """
    Event Confidence Score (0-100) for hackathon alignment.
    Formula: higher when event is closer; national events get a small boost.
    Replace with SageMaker/weighted model in production.
    """
    if days_until_event <= 0:
        return 100
    # Closer = higher: 14 days -> lower, 1 day -> high
    proximity = max(0, 14 - days_until_event) * 6  # 0-84
    base = 40
    type_bonus = 10 if (event_type or "").lower() in ("national", "festival") else 0
    score = base + proximity + type_bonus
    return min(100, max(0, score))


S3     = boto3.client("s3")
DYNAMO = boto3.resource("dynamodb")


def get_s3_json(bucket, key):
    try:
        resp = S3.get_object(Bucket=bucket, Key=key)
        return json.loads(resp["Body"].read().decode())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "NoSuchBucket"):
            print(f"S3 key not found: s3://{bucket}/{key}")
            return {}
        raise


def get_all_users():
    table = DYNAMO.Table(USERS_TABLE)
    try:
        resp = table.scan(
            ProjectionExpression="user_id, #st, city, phone, alert_days_before, alert_time_hour_ist",
            ExpressionAttributeNames={"#st": "state"}
        )
        return resp.get("Items", [])
    except Exception as e:
        print(f"DynamoDB scan failed: {e}")
        return []


def days_until(date_str, today_ist):
    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (event_date - today_ist.date()).days


def build_hinglish_message(event_name, days):
    key = event_name.lower()
    base = None
    for k, msg in FESTIVAL_MESSAGES.items():
        if k in key or key in k:
            base = msg
            break
    if not base:
        base = GENERIC_MESSAGE.format(name=event_name)

    if days == 1:
        time_prefix = "Kal hai!"
    elif days <= 3:
        time_prefix = f"Sirf {days} din bache hain!"
    else:
        time_prefix = f"{days} din baad aa raha hai!"
    return f"🎉 {time_prefix} {base}"


def is_kirana_relevant(title):
    """Check if a news headline is relevant to a Kirana store owner."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in RELEVANT_KEYWORDS)


def get_kirana_news():
    """
    Fetch Kirana/FMCG relevant news from multiple RSS feeds.
    Filters headlines to only those relevant to small shopkeepers.
    Falls back to commodity news if nothing relevant found.
    """
    all_headlines = []

    for rss_url in NEWS_RSS_URLS:
        try:
            req = urllib.request.Request(
                rss_url,
                headers={"User-Agent": "Mozilla/5.0 (AISahayak/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=6) as r:
                xml_data = r.read()
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            for item in items[:10]:
                title = item.findtext("title", "").strip()
                title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                if title:
                    all_headlines.append(title)
        except Exception as e:
            print(f"RSS fetch failed for {rss_url}: {e}")
            continue

    # First try: find a Kirana-relevant headline
    for headline in all_headlines:
        if is_kirana_relevant(headline):
            return f"📰 Dukaan ke liye khabar: {headline}"

    # Fallback: return first available headline with a generic prefix
    if all_headlines:
        return f"📰 Aaj ki vyapar khabar: {all_headlines[0]}"

    return None


def post_to_webhook(webhook_url, payload):
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(f"Webhook POST failed: {e}")
        return False


def _check_change_calendar_open() -> bool:
    """If SSM Change Calendar is configured, only proceed when state is OPEN (digital Panchang)."""
    if not SSM_CALENDAR_NAME:
        return True
    try:
        ssm = boto3.client("ssm")
        out = ssm.get_calendar_state(CalendarNames=[SSM_CALENDAR_NAME])
        state = (out.get("State") or "CLOSED").upper()
        print(f"Change Calendar {SSM_CALENDAR_NAME} state: {state}")
        return state == "OPEN"
    except Exception as e:
        print(f"Change Calendar check failed: {e}, proceeding anyway")
        return True


def handler(event, context):
    if not CALENDAR_S3_BUCKET:
        print("ERROR: CALENDAR_S3_BUCKET env var not set")
        return {"statusCode": 400, "body": "CALENDAR_S3_BUCKET not set"}

    if not _check_change_calendar_open():
        print("Change Calendar state is CLOSED; skipping run (digital Panchang)")
        return {"statusCode": 200, "body": json.dumps({"skipped": True, "reason": "change_calendar_closed"})}

    now_utc    = datetime.utcnow()
    today_ist  = now_utc + timedelta(hours=5, minutes=30)
    print(f"Running for IST date: {today_ist.date()}")

    national_data   = get_s3_json(CALENDAR_S3_BUCKET, NATIONAL_S3_KEY)
    national_events = national_data.get("events", [])
    print(f"Loaded {len(national_events)} national events")

    users = get_all_users()
    print(f"Found {len(users)} users in DynamoDB")

    # Fetch Kirana-relevant news once (shared across all users)
    news_headline = get_kirana_news()
    print(f"News: {news_headline}")

    summary = {
        "date_ist": str(today_ist.date()),
        "users_processed": len(users),
        "total_alerts_sent": 0,
        "news": news_headline,
        "per_user": [],
    }

    current_ist_hour = today_ist.hour  # 0-23, so each user gets alerts only at their chosen hour

    for user in users:
        user_id    = user.get("user_id", "unknown")
        state_code = (user.get("state") or "").upper()
        city       = user.get("city", "")

        # ── Hour filter: only send alerts at the user's chosen alert_time_hour_ist ──
        try:
            user_alert_hour = int(user.get("alert_time_hour_ist") or DEFAULT_ALERT_HOUR_IST)
        except (TypeError, ValueError):
            user_alert_hour = DEFAULT_ALERT_HOUR_IST
        if current_ist_hour != user_alert_hour:
            print(f"User {user_id}: skip (wants {user_alert_hour}:00 IST, now {current_ist_hour}:00)")
            summary["per_user"].append({
                "user_id": user_id,
                "state": state_code,
                "city": city,
                "alert_days_before": int(user.get("alert_days_before") or DEFAULT_ALERT_DAYS),
                "alerts": 0,
                "skipped": True,
                "reason": "hour_mismatch",
            })
            continue

        # ── Per-user alert window (user can customize this!) ──────────────
        user_alert_days = int(user.get("alert_days_before") or DEFAULT_ALERT_DAYS)
        print(f"User {user_id} alert window: {user_alert_days} days")

        # Regional calendar
        regional_events = []
        region_suffix   = STATE_CODE_MAP.get(state_code)
        if region_suffix:
            regional_key    = f"{REGIONAL_S3_PREFIX}{region_suffix}.json"
            regional_data   = get_s3_json(CALENDAR_S3_BUCKET, regional_key)
            regional_events = regional_data.get("events", [])
            print(f"User {user_id} ({state_code}) — {len(regional_events)} regional events")
        else:
            print(f"User {user_id} — no regional map for '{state_code}', national only")

        all_events  = national_events + regional_events
        user_alerts = []

        for ev in all_events:
            date_str = ev.get("date")
            if not date_str:
                continue
            days = days_until(date_str, today_ist)

            # Use event-specific alert_days if present, else user's personal window
            alert_days = ev.get("alert_days")
            should_alert = (
                (alert_days and days in alert_days) or
                (not alert_days and 0 < days <= user_alert_days)
            )

            if should_alert:
                message  = build_hinglish_message(ev.get("name", "Event"), days)
                stock    = ev.get("stock_hint", "")
                confidence = event_confidence_score(days, ev.get("type", "festival"))
                full_msg = f"{message}\n💡 Stock tip: {stock}" if stock else message
                print(f"ALERT for {user_id}: '{ev.get('name')}' in {days} days (confidence {confidence}%)")

                sent = False
                if BACKEND_WEBHOOK_URL:
                    sent = post_to_webhook(BACKEND_WEBHOOK_URL, {
                        "user_id":    user_id,
                        "phone":      user.get("phone", ""),
                        "text":       full_msg,
                        "platform":   "whatsapp",
                        "is_alert":   True,
                        "alert_type": ev.get("type", "festival"),
                        "event_name": ev.get("name", ""),
                        "days_until": days,
                        "event_confidence_score": confidence,
                    })

                user_alerts.append({
                    "event":     ev.get("name"),
                    "days_until": days,
                    "message":   full_msg,
                    "sent":      sent,
                })

        if news_headline and BACKEND_WEBHOOK_URL:
            post_to_webhook(BACKEND_WEBHOOK_URL, {
                "user_id":    user_id,
                "phone":      user.get("phone", ""),
                "text":       news_headline,
                "platform":   "whatsapp",
                "is_alert":   True,
                "alert_type": "news",
            })

        summary["total_alerts_sent"] += len(user_alerts)
        summary["per_user"].append({
            "user_id":           user_id,
            "state":             state_code,
            "city":              city,
            "alert_days_before": user_alert_days,
            "alerts":            len(user_alerts),
        })
        print(f"User {user_id}: {len(user_alerts)} alerts sent")

    print(f"Done: {summary['total_alerts_sent']} total alerts across {len(users)} users")
    return {"statusCode": 200, "body": json.dumps(summary, ensure_ascii=False)}
