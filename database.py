from supabase import create_client, Client
from postgrest.exceptions import APIError
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client if credentials are available
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fallback in-memory storage
messages = []
meetings = []


def insert_message(data):
    print("[INSERTING MESSAGE]", data)  # Add logging
    if supabase:
        # Convert datetime to string for JSON serialization
        if 'timestamp' in data and hasattr(data['timestamp'], 'isoformat'):
            data['timestamp'] = data['timestamp'].isoformat()
        try:
            return supabase.table("messages").insert(data).execute()
        except APIError as e:
            print(f"[SUPABASE RLS ERROR]: {e}")
            # Fall back to in-memory storage
            messages.append(data)
            return {"data": [data]}
    else:
        messages.append(data)
        return {"data": [data]}


def get_all_messages():
    if supabase:
        res = supabase.table("messages").select("*").order("timestamp", desc=False).execute()
        return res.data
    else:
        return messages


def insert_meeting(data):
    print("[INSERTING MEETING]", data)  # Add logging
    if supabase:
        # Convert any datetime fields to string for JSON serialization
        for key, value in data.items():
            if hasattr(value, 'isoformat'):
                data[key] = value.isoformat()
        try:
            return supabase.table("meetings").insert(data).execute()
        except APIError as e:
            print(f"[SUPABASE RLS ERROR]: {e}")
            # Fall back to in-memory storage
            meetings.append(data)
            return {"data": [data]}
    else:
        meetings.append(data)
        return {"data": [data]}


def get_meetings():
    if supabase:
        res = supabase.table("meetings").select("*").order("date", desc=False).execute()
        return res.data
    else:
        return meetings
