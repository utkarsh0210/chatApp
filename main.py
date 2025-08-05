from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from models import Message, Meeting
from database import insert_message, get_all_messages, insert_meeting, get_meetings
from mailer import send_meeting_email


app = FastAPI()

origins = ["*"]  # For testing, allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store all connected clients
connected_clients = set()


@app.get("/messages")
async def fetch_messages():
    return get_all_messages()


@app.post("/message")
async def send_message(msg: Message):
    msg_data = msg.dict()
    msg_data["timestamp"] = msg_data.get("timestamp") or datetime.utcnow().isoformat()
    insert_message(msg_data)
    await broadcast(msg_data)
    return {"status": "sent"}


@app.get("/meetings")
async def fetch_meetings():
    return get_meetings()


@app.post("/schedule")
async def schedule_meeting(meeting: Meeting):
    insert_meeting(meeting.dict())

    # Prepare and send email
    subject = f"📅 Meeting Scheduled: {meeting.title}"
    body = f"Hello,\n\nYou have a meeting scheduled.\n\nTitle: {meeting.title}\nDate: {meeting.date}\nTime: {meeting.time}\n\nRegards,\nMeeting Scheduler App"
    send_meeting_email(subject, body, meeting.participants)

    return {"status": "scheduled and emailed"}


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # Save message to database
            insert_message(data)
            await broadcast(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def broadcast(message: dict):
    to_remove = set()
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            to_remove.add(client)
    connected_clients.difference_update(to_remove)
