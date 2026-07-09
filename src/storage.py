import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "fruit_bot_data"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def save_result(record):
    row = {
        "fill_level": record["fill_level"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _get_client().table(TABLE_NAME).insert(row).execute()
