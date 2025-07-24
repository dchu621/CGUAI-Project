# calendar_scheduler.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = FastAPI()

# Google Calendar 設定
TIME_ZONE = 'Asia/Taipei'
CREDENTIALS_FILE = 'credentials.json'

# 載入憑證
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/calendar']
)
service = build('calendar', 'v3', credentials=creds)

# 請求格式
class EventRequest(BaseModel):
    date: str  # e.g. "2025-07-02"
    time: str  # e.g. "15:00"
    title: str

@app.post("/mcp/calendar_scheduler")
def create_event(req: EventRequest):
    try:
        start_dt = datetime.strptime(f"{req.date} {req.time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=1)

        event = {
            'summary': req.title,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': TIME_ZONE},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': TIME_ZONE},
        }

        event_result = service.events().insert(calendarId='dchu0621@gmail.com', body=event).execute()
        return {"status": "success", "eventLink": event_result.get('htmlLink')}

    except Exception as e:
        return {"status": "error", "message": str(e)}
