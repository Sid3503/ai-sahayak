import argparse
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LAMBDA_ENV = BASE_DIR / "aws" / "lambda" / "lambda-env.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write AI_SAHAYAK_CALENDAR_EVENTS_JSON into aws/lambda/lambda-env.json")
    parser.add_argument("--calendar-json", required=True, help="Calendar env JSON string emitted by provision_change_calendars.py")
    args = parser.parse_args()

    env_path = LAMBDA_ENV
    data = {"Variables": {}}
    if env_path.exists():
        data = json.loads(env_path.read_text(encoding="utf-8"))
    data.setdefault("Variables", {})
    data["Variables"]["AI_SAHAYAK_CALENDAR_EVENTS_JSON"] = args.calendar_json
    env_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Updated {env_path}")


if __name__ == "__main__":
    main()
