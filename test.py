from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

data = {"user_id": 1, "event_type": "page_view", "page_url": "/home", "metadata": {}}
supabase.table("activity_log").insert(data).execute()
