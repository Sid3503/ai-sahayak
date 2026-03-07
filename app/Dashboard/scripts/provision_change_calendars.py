import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = BASE_DIR / "config" / "festival_catalog.json"
GENERATED_DIR = BASE_DIR / "generated" / "calendars"


def resolve_aws_cli() -> str:
    candidates = [
        os.getenv("AWS_CLI_PATH", "").strip(),
        shutil.which("aws") or "",
        r"C:\Program Files\Amazon\AWSCLIV2\aws.exe",
        r"C:\Program Files (x86)\Amazon\AWSCLIV2\aws.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    raise FileNotFoundError(
        "AWS CLI not found. Install AWS CLI v2 or set AWS_CLI_PATH to the full aws.exe path."
    )


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _slug(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum() or ch in ("-", "_")).strip() or "festival"


def _event_uid(calendar_name: str, day: str) -> str:
    return f"{_slug(calendar_name)}-{day}@ai-sahayak"


def _ics_header() -> List[str]:
    return [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Sahayak//Festival Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:AI Sahayak Festival Calendar",
    ]


def _ics_footer() -> List[str]:
    return ["END:VCALENDAR"]


def _render_event_lines(calendar_name: str, festival_name: str, start_day: date, duration_days: int) -> List[str]:
    end_day = start_day + timedelta(days=max(1, duration_days))
    created = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return [
        "BEGIN:VEVENT",
        f"UID:{_event_uid(calendar_name, start_day.isoformat())}",
        f"DTSTAMP:{created}",
        f"DTSTART;VALUE=DATE:{start_day.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{end_day.strftime('%Y%m%d')}",
        f"SUMMARY:{festival_name}",
        f"DESCRIPTION:AI Sahayak managed calendar event for {festival_name}",
        "END:VEVENT",
    ]


def write_calendar_ics(festival: Dict[str, Any], default_duration_days: int, out_dir: Path) -> Path:
    calendar_name = str(festival["calendar_name"])
    festival_name = str(festival["name"])
    duration_days = int(festival.get("duration_days", default_duration_days))
    lines = _ics_header()
    for raw_day in festival.get("dates", []):
        if not raw_day:
            continue
        day = date.fromisoformat(str(raw_day))
        lines.extend(_render_event_lines(calendar_name, festival_name, day, duration_days))
    lines.extend(_ics_footer())
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{calendar_name}.ics"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def aws_cli(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    aws_exe = resolve_aws_cli()
    full_args = [aws_exe, *args]
    return subprocess.run(full_args, check=check, capture_output=True, text=True)


def ensure_calendar_document(calendar_name: str, ics_path: Path, region: str) -> str:
    content_text = ics_path.read_text(encoding="utf-8")
    describe = aws_cli(
        [
            "ssm",
            "describe-document",
            "--name",
            calendar_name,
            "--region",
            region,
        ],
        check=False,
    )

    if describe.returncode == 0:
        update = aws_cli(
            [
                "ssm",
                "update-document",
                "--name",
                calendar_name,
                "--document-format",
                "TEXT",
                "--content",
                content_text,
                "--document-version",
                "$LATEST",
                "--region",
                region,
            ],
            check=False,
        )
        if update.returncode != 0:
            stderr = (update.stderr or "").strip()
            if "DuplicateDocumentContent" not in stderr:
                raise subprocess.CalledProcessError(update.returncode, update.args, output=update.stdout, stderr=update.stderr)
    else:
        stderr = (describe.stderr or "").strip()
        if "InvalidDocument" not in stderr and "does not exist" not in stderr:
            raise subprocess.CalledProcessError(describe.returncode, describe.args, output=describe.stdout, stderr=describe.stderr)
        aws_cli(
            [
                "ssm",
                "create-document",
                "--name",
                calendar_name,
                "--document-format",
                "TEXT",
                "--document-type",
                "ChangeCalendar",
                "--content",
                content_text,
                "--region",
                region,
            ]
        )

    doc = aws_cli(
        [
            "ssm",
            "describe-document",
            "--name",
            calendar_name,
            "--region",
            region,
            "--query",
            "Document.Description.Name",
            "--output",
            "text",
        ]
    )
    if doc.returncode != 0:
        raise RuntimeError(f"Failed to confirm calendar document {calendar_name}: {doc.stderr}")

    account = aws_cli(
        [
            "sts",
            "get-caller-identity",
            "--query",
            "Account",
            "--output",
            "text",
        ]
    )
    if account.returncode != 0:
        raise RuntimeError(f"Failed to resolve AWS account id: {account.stderr}")
    return f"arn:aws:ssm:{region}:{account.stdout.strip()}:document/{calendar_name}"


def build_calendar_env_payload(festivals: List[Dict[str, Any]], region: str, calendar_arns: Dict[str, str]) -> str:
    payload = []
    for festival in festivals:
        calendar_name = str(festival["calendar_name"])
        payload.append(
            {
                "name": festival["name"],
                "calendar_arn": calendar_arns[calendar_name],
                "boost": float(festival["boost"]),
                "promo_depth_pct": float(festival["promo_depth_pct"]),
                "pre_window_days": int(festival.get("pre_window_days", 0)),
                "pre_window_boost": float(festival.get("pre_window_boost", 1.0)),
            }
        )
    return json.dumps(payload, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision AWS Systems Manager Change Calendars from festival catalog.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Path to festival catalog JSON.")
    parser.add_argument("--region", default="ap-south-1", help="AWS region.")
    parser.add_argument("--write-only", action="store_true", help="Only write ICS files, do not call AWS.")
    parser.add_argument("--out-dir", default=str(GENERATED_DIR), help="Directory to write generated ICS files.")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    out_dir = Path(args.out_dir)
    catalog = _load_json(catalog_path)
    festivals = catalog.get("festivals", [])
    default_duration_days = int(catalog.get("default_event_duration_days", 1))

    if not festivals:
        raise SystemExit("No festivals found in catalog.")

    calendar_arns: Dict[str, str] = {}
    written_paths = []
    for festival in festivals:
        ics_path = write_calendar_ics(festival, default_duration_days, out_dir)
        written_paths.append(str(ics_path))
        calendar_name = str(festival["calendar_name"])
        if args.write_only:
            calendar_arns[calendar_name] = f"arn:aws:ssm:{args.region}:YOUR_ACCOUNT_ID:document/{calendar_name}"
        else:
            calendar_arns[calendar_name] = ensure_calendar_document(calendar_name, ics_path, args.region)

    env_json = build_calendar_env_payload(festivals, args.region, calendar_arns)
    print("Generated ICS files:")
    for path in written_paths:
        print(f" - {path}")
    print("\nAI_SAHAYAK_CALENDAR_EVENTS_JSON=")
    print(env_json)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print("AWS CLI command failed.", file=sys.stderr)
        print(f"Command: {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(f"STDOUT:\n{exc.stdout}", file=sys.stderr)
        if exc.stderr:
            print(f"STDERR:\n{exc.stderr}", file=sys.stderr)
        raise
