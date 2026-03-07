# Load .env into os.environ so boto3/Bedrock see AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
import os
from pathlib import Path
def _load_env():
    from dotenv import load_dotenv
    # Try agents dir (when running as python src/ai_sahayak/main.py from agents/)
    agents_dir = Path(__file__).resolve().parents[2]
    load_dotenv(agents_dir / ".env")
    load_dotenv(Path.cwd() / ".env")  # Then cwd
_load_env()

import uvicorn
from ai_sahayak.api.server import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("ai_sahayak.main:app", host="0.0.0.0", port=8000, reload=True)
