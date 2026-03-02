"""
Indian identifier and location validators for AI Sahayak onboarding.
Validates Aadhar, GST, PIN code, and geographic coordinates.
"""
import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    normalized: str | None  # cleaned, canonical value on success
    error: str | None       # human-readable error on failure


# ---------------------------------------------------------------------------
# Aadhar
# ---------------------------------------------------------------------------

def validate_aadhar(raw: str) -> ValidationResult:
    """
    Strip all non-numeric characters, then ensure exactly 12 digits remain.
    Accepts inputs like '5289 1204 8623' or '528912048623'.
    """
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 12:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"Aadhar must be exactly 12 digits (got {len(digits)}).",
        )
    return ValidationResult(is_valid=True, normalized=digits, error=None)


# ---------------------------------------------------------------------------
# GST
# ---------------------------------------------------------------------------

# Valid Indian GST state codes 01-37
_VALID_STATE_CODES = {str(i).zfill(2) for i in range(1, 38)}

# 2 digits (state) + 10 alphanumeric (PAN) + 1 digit + 1 alphanumeric + 1 alphanumeric
_GST_RE = re.compile(r"^(\d{2})([A-Z0-9]{10})(\d)([A-Z0-9])([A-Z0-9])$")


def validate_gst(raw: str) -> ValidationResult:
    """
    Strip non-alphanumeric chars, uppercase, then check GST-IN structure and state code.
    """
    cleaned = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if len(cleaned) != 15:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"GST number must be 15 alphanumeric characters (got {len(cleaned)}).",
        )
    match = _GST_RE.match(cleaned)
    if not match:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error="GST number format is invalid. Expected: 2-digit state + 10-char PAN + 1 digit + 2 alphanumeric.",
        )
    state_code = match.group(1)
    if state_code not in _VALID_STATE_CODES:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"GST state code '{state_code}' is out of the valid range (01–37).",
        )
    return ValidationResult(is_valid=True, normalized=cleaned, error=None)


# ---------------------------------------------------------------------------
# PIN Code
# ---------------------------------------------------------------------------

_PINCODE_RE = re.compile(r"^[1-9]\d{5}$")


def validate_pincode(raw: str) -> ValidationResult:
    """
    Strip non-digits, ensure 6 digits where the first is 1-9.
    """
    digits = re.sub(r"\D", "", raw)
    if not _PINCODE_RE.match(digits):
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error="PIN code must be 6 digits and must not start with 0.",
        )
    return ValidationResult(is_valid=True, normalized=digits, error=None)


# ---------------------------------------------------------------------------
# Geographic Coordinates (India bounding box)
# ---------------------------------------------------------------------------

_LAT_RANGE = (6.4, 37.6)   # degrees N
_LON_RANGE = (68.7, 97.25)  # degrees E

# Matches optional sign, digits, optional decimal
_COORD_RE = re.compile(r"^([+-]?\d+\.?\d*)$")


def validate_coordinates(lat_raw: str, lon_raw: str) -> ValidationResult:
    """
    Validate that a latitude/longitude pair lies within India's bounding box.
    Both arguments should be plain decimal-degree strings.
    """
    lat_match = _COORD_RE.match(lat_raw.strip())
    lon_match = _COORD_RE.match(lon_raw.strip())

    if not lat_match or not lon_match:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error="Coordinates must be plain decimal-degree numbers (e.g. '18.9750,72.8258').",
        )

    lat = float(lat_raw)
    lon = float(lon_raw)

    if not (_LAT_RANGE[0] <= lat <= _LAT_RANGE[1]):
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"Latitude {lat} is outside India's range ({_LAT_RANGE[0]}°N – {_LAT_RANGE[1]}°N).",
        )
    if not (_LON_RANGE[0] <= lon <= _LON_RANGE[1]):
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"Longitude {lon} is outside India's range ({_LON_RANGE[0]}°E – {_LON_RANGE[1]}°E).",
        )
    return ValidationResult(
        is_valid=True,
        normalized=f"{lat},{lon}",
        error=None,
    )


# ---------------------------------------------------------------------------
# Convenience dispatcher used by onboarding node
# ---------------------------------------------------------------------------

def validate_onboarding_field(field: str, value: str) -> ValidationResult:
    """
    Validate a single onboarding field by name.
    Returns ValidationResult. Skips validation for unknown / non-identifiable fields.
    """
    if not value or str(value).strip().lower() in {"null", "none", "not provided", "", "unknown"}:
        return ValidationResult(is_valid=True, normalized=value, error=None)  # nothing to validate yet

    handlers = {
        "aadhar": validate_aadhar,
        "pincode": validate_pincode,
        "gst_number": _validate_gst_lenient,
    }
    handler = handlers.get(field)
    if handler is None:
        return ValidationResult(is_valid=True, normalized=value, error=None)
    return handler(value)


def _validate_gst_lenient(raw: str) -> ValidationResult:
    """
    GST is optional – 'No' / 'None' / 'No GST' answers are always valid.
    Only run full structural validation when the user explicitly provides a number.
    """
    normalized = raw.strip().lower()
    negative_patterns = {"no", "none", "na", "n/a", "no gst", "nahi", "नहीं"}
    if any(normalized.startswith(neg) for neg in negative_patterns) or normalized in negative_patterns:
        return ValidationResult(is_valid=True, normalized="No", error=None)
    return validate_gst(raw)
