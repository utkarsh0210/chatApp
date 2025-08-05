from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    name: str
    email: str
    content: str
    timestamp: Optional[datetime] = None


class Meeting(BaseModel):
    title: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    participants: List[str]
