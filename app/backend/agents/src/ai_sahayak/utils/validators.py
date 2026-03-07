"""
Indian identifier and location validators for AI Sahayak onboarding.
Validates Aadhar, GST, PIN code, and geographic coordinates.
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    is_valid: bool
    normalized: Optional[str]
    error: Optional[str]


def validate_aadhar(raw: str) -> ValidationResult:
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 12:
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error=f"Aadhar must be exactly 12 digits (got {len(digits)}).",
        )
    return ValidationResult(is_valid=True, normalized=digits, error=None)


_VALID_STATE_CODES = {str(i).zfill(2) for i in range(1, 38)}
_GST_RE = re.compile(r"^(\d{2})([A-Z0-9]{10})(\d)([A-Z0-9])([A-Z0-9])$")


def validate_gst(raw: str) -> ValidationResult:
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


_PINCODE_RE = re.compile(r"^[1-9]\d{5}$")


def validate_pincode(raw: str) -> ValidationResult:
    digits = re.sub(r"\D", "", raw)
    if not _PINCODE_RE.match(digits):
        return ValidationResult(
            is_valid=False,
            normalized=None,
            error="PIN code must be 6 digits and must not start with 0.",
        )
    return ValidationResult(is_valid=True, normalized=digits, error=None)


def _validate_gst_lenient(raw: str) -> ValidationResult:
    normalized = raw.strip().lower()
    negative_patterns = {"no", "none", "na", "n/a", "no gst", "nahi", "नहीं"}
    if any(normalized.startswith(neg) for neg in negative_patterns) or normalized in negative_patterns:
        return ValidationResult(is_valid=True, normalized="No", error=None)
    return validate_gst(raw)


def validate_onboarding_field(field: str, value: str) -> ValidationResult:
    if not value or str(value).strip().lower() in {"null", "none", "not provided", "", "unknown"}:
        return ValidationResult(is_valid=True, normalized=value, error=None)

    handlers = {
        "aadhar": validate_aadhar,
        "pincode": validate_pincode,
        "gst_number": _validate_gst_lenient,
    }
    handler = handlers.get(field)
    if handler is None:
        return ValidationResult(is_valid=True, normalized=value, error=None)
    return handler(value)
