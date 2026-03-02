"""
Location enrichment for AI Sahayak.

Resolves user-provided location inputs (PIN codes, lat/lon coordinates, or
free-text addresses) into a rich, human-readable string before storing in
DynamoDB.

Resolution strategy (in priority order):
  1. If input is a 6-digit Indian PIN code  →  India Post API (no key needed)
  2. If input looks like lat,lon coordinates →  Nominatim reverse-geocoding
  3. Otherwise                               →  return raw input (best-effort)
"""
import re
import httpx
import asyncio
from typing import Optional

_PINCODE_RE = re.compile(r"^\d{6}$")
_COORD_RE = re.compile(r"^([+-]?\d+\.?\d*)\s*,\s*([+-]?\d+\.?\d*)$")

# Public India Post API – no auth required
_INDIA_POST_URL = "https://api.postalpincode.in/pincode/{pin}"
# Nominatim (OpenStreetMap) reverse-geocoding – free, no key needed
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

_NOMINATIM_HEADERS = {"User-Agent": "AISahayak/1.0 (contact@ai-sahayak.in)"}
_HTTP_TIMEOUT = 8.0


async def _resolve_by_pincode(pincode: str) -> Optional[str]:
    """
    Query India Post API to convert a PIN to 'City, District, State' string.
    Returns None on failure so caller can fall back gracefully.
    """
    url = _INDIA_POST_URL.format(pin=pincode)
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        if not data or data[0].get("Status") != "Success":
            return None

        post_offices = data[0].get("PostOffice", [])
        if not post_offices:
            return None

        # Take the first post office entry as the canonical reference
        office = post_offices[0]
        parts = [
            office.get("Block") or office.get("Name"),
            office.get("District"),
            office.get("State"),
        ]
        location_str = ", ".join(p for p in parts if p)
        return f"{location_str} - {pincode}" if location_str else None

    except Exception as exc:
        print(f"[LocationResolver] PIN code API error for {pincode}: {exc}")
        return None


async def _resolve_by_coordinates(lat: str, lon: str) -> Optional[str]:
    """
    Reverse-geocode a lat/lon pair via Nominatim.
    Returns a human-readable location string or None on failure.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 14,         # neighbourhood level
        "addressdetails": 1,
    }
    try:
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
    """
    Main entry point.

    Accepts any of the following and returns the best available
    human-readable location string:
      - '400001'                  → 'Bandra, Mumbai Suburban, Maharashtra - 400001'
      - '18.9750, 72.8258'       → 'Bandra West, Mumbai, Maharashtra, India - 400050'
      - 'shared location'         → 'shared location'  (unchanged, best-effort)
      - None / empty              → 'Unknown Location'
    """
    if not raw_input or str(raw_input).strip().lower() in {
        "null", "none", "not provided", "", "unknown", "unknown location"
    }:
        return "Unknown Location"

    cleaned = raw_input.strip()

    # --- PIN code ---
    digits_only = re.sub(r"\D", "", cleaned)
    if _PINCODE_RE.match(digits_only):
        resolved = await _resolve_by_pincode(digits_only)
        if resolved:
            return resolved

    # --- lat,lon coordinates ---
    coord_match = _COORD_RE.match(cleaned)
    if coord_match:
        lat, lon = coord_match.group(1), coord_match.group(2)
        resolved = await _resolve_by_coordinates(lat, lon)
        if resolved:
            return resolved

    # --- Fallback: check if a 6-digit number is embedded anywhere in the string ---
    embedded = re.search(r"\b([1-9]\d{5})\b", cleaned)
    if embedded:
        resolved = await _resolve_by_pincode(embedded.group(1))
        if resolved:
            return resolved

    # --- Give up: return whatever the user typed ---
    return cleaned or "Unknown Location"
