#!/bin/bash
# Upload missing regional panchang JSON files to S3 (panchang/).
# Demo users: raju/ramesh=MP, suresh=RJ, kanta=GJ, lakshmi=TS → need RJ + ap_ts.
# Run from repo root or set SCRIPT_DIR. Bucket: ai-sahayak-calendar (or CALENDAR_BUCKET).

set -e
BUCKET="${CALENDAR_BUCKET:-ai-sahayak-calendar}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_FESTIVALS="${SCRIPT_DIR}/../app/backend/agents/src/ai_sahayak/knowledge_base/festivals"
PREFIX="panchang"

echo "Using bucket: $BUCKET"

# Upload from repo if files exist
for f in regional_rj.json regional_ap_ts.json; do
  if [ -f "$REPO_FESTIVALS/$f" ]; then
    # Skip empty {} (ap_ts in repo is empty)
    if [ -s "$REPO_FESTIVALS/$f" ] && [ "$(cat "$REPO_FESTIVALS/$f")" != "{}" ]; then
      aws s3 cp "$REPO_FESTIVALS/$f" "s3://$BUCKET/$PREFIX/$f" --content-type application/json
      echo "Uploaded $f from repo"
    fi
  fi
done

# If regional_ap_ts.json missing or empty, create minimal and upload
if ! aws s3 ls "s3://$BUCKET/$PREFIX/regional_ap_ts.json" &>/dev/null || \
   [ "$(aws s3 cp "s3://$BUCKET/$PREFIX/regional_ap_ts.json" - 2>/dev/null)" = "{}" ]; then
  echo "Creating minimal regional_ap_ts.json for Telangana/AP (Hyderabad — lakshmi)"
  cat << 'APTS_JSON' > /tmp/regional_ap_ts.json
{
  "state": "Telangana / Andhra Pradesh",
  "state_code": "ap_ts",
  "cities": ["Hyderabad", "Secunderabad", "Warangal", "Vijayawada", "Visakhapatnam"],
  "description": "Regional festivals for Telangana and AP shopkeepers",
  "events": [
    { "id": "ap_ts-ugadi-2026",        "name": "Ugadi",                    "date": "2026-03-30", "type": "regional", "alert_days": [7,5,3,1], "stock_hint": "Oggu, Sweets, New clothes, Mango — New Year" },
    { "id": "ap_ts-bathukamma-2026",   "name": "Bathukamma (TS)",           "date": "2026-10-08", "type": "regional", "alert_days": [7,5,3,1], "stock_hint": "Flowers, Bangles, Sarees, Sweets — women's festival" },
    { "id": "ap_ts-bonalu-2026",       "name": "Bonalu (Hyderabad)",        "date": "2026-07-19", "type": "local",    "alert_days": [7,3,1],   "stock_hint": "Rice, Jaggery, Fruits, Puja items" },
    { "id": "ap_ts-diwali-2026",       "name": "Diwali (AP/TS)",             "date": "2026-11-08", "type": "regional", "alert_days": [14,7,5,3,1], "stock_hint": "Sweets, Dry fruits, Diyas, Fireworks, Gift packs" },
    { "id": "ap_ts-ganesh-chaturthi-2026", "name": "Ganesh Chaturthi (AP/TS)", "date": "2026-09-10", "type": "regional", "alert_days": [7,5,3,1], "stock_hint": "Modak, Coconut, Flowers, Incense — big in Hyderabad" }
  ]
}
APTS_JSON
  aws s3 cp /tmp/regional_ap_ts.json "s3://$BUCKET/$PREFIX/regional_ap_ts.json" --content-type application/json
  echo "Uploaded regional_ap_ts.json (minimal)"
fi

echo "Listing panchang/ objects:"
aws s3 ls "s3://$BUCKET/$PREFIX/"
