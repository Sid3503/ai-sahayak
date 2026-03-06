"""
Location enrichment for AI Sahayak.
Resolves PIN codes or lat,lon into a human-readable string before storing in DynamoDB.
"""
import re
from typing import Optional

_PINCODE_RE = re.compile(r"^\d{6}$")
_COORD_RE = re.compile(r"^([+-]?\d+\.?\d*)\s*,\s*([+-]?\d+\.?\d*)$")

_INDIA_POST_URL = "https://api.postalpincode.in/pincode/{pin}"
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
_NOMINATIM_HEADERS = {"User-Agent": "AISahayak/1.0 (contact@ai-sahayak.in)"}
_HTTP_TIMEOUT = 8.0


async def _resolve_by_pincode(pincode: str) -> Optional[str]:
    url = _INDIA_POST_URL.format(pin=pincode)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        if not data or data[0].get("Status") != "Success":
            return None

        post_offices = data[0].get("PostOffice", [])
        if not post_offices:
            return None

        BRANCH_PRIORITY = {
            "Head Post Office": 0,
            "Sub Post Office": 1,
            "Branch Post Office": 2,
        }
        sorted_offices = sorted(
            post_offices,
            key=lambda x: BRANCH_PRIORITY.get(x.get("BranchType", ""), 99)
        )
        office = sorted_offices[0]
        name = office.get("Name", "")
        name = re.sub(r'\s*\([^)]+\)\s*$', '', name)
        parts = [
            name if name and name.upper() != "NA" else None,
            office.get("District"),
            office.get("State"),
        ]
        location_str = ", ".join(p for p in parts if p)
        return f"{location_str} - {pincode}" if location_str else None

    except Exception as exc:
        print(f"[LocationResolver] PIN code API error for {pincode}: {exc}")
        return None


async def _resolve_by_coordinates(lat: str, lon: str) -> Optional[str]:
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 14,
        "addressdetails": 1,
    }
    try:
        import httpx
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=_NOMINATIM_HEADERS) as client:
            resp = await client.get(_NOMINATIM_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        addr = data.get("address", {})
        parts = [
            addr.get("suburb") or addr.get("neighbourhood") or addr.get("village"),
            addr.get("city") or addr.get("town") or addr.get("county"),
            addr.get("state"),
            addr.get("country"),
        ]
        location_str = ", ".join(p for p in parts if p)
        postcode = addr.get("postcode", "")
        return f"{location_str} - {postcode}" if postcode else location_str or None

    except Exception as exc:
        print(f"[LocationResolver] Nominatim error for {lat},{lon}: {exc}")
        return None


async def enrich_location(raw_input: str) -> str:
    if not raw_input or str(raw_input).strip().lower() in {
        "null", "none", "not provided", "", "unknown", "unknown location"
    }:
        return "Unknown Location"

    cleaned = raw_input.strip()

    digits_only = re.sub(r"\D", "", cleaned)
    if _PINCODE_RE.match(digits_only):
        resolved = await _resolve_by_pincode(digits_only)
        if resolved:
            return resolved

    coord_match = _COORD_RE.match(cleaned)
    if coord_match:
        lat, lon = coord_match.group(1), coord_match.group(2)
        resolved = await _resolve_by_coordinates(lat, lon)
        if resolved:
            return resolved

    embedded = re.search(r"\b([1-9]\d{5})\b", cleaned)
    if embedded:
        resolved = await _resolve_by_pincode(embedded.group(1))
        if resolved:
            return resolved

    return cleaned or "Unknown Location"
