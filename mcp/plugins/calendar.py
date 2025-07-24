from mcp.base import MCPAgent
from mcp.utils.time_extractor import extract_event
import requests

class CalendarPlugin(MCPAgent):
    def __init__(self):
        super().__init__(
            name="calendar_scheduler",
            description="從自然語言中擷取排程資訊並新增到 Google Calendar"
        )

    def match(self, text: str) -> bool:
        return extract_event(text) is not None

    def run(self, text: str, context: dict = {}) -> dict:
        event = extract_event(text)
        if not event:
            return {
                "status": "fail",
                "plugin": "calendar",
                "reason": "no_event_detected",
                "message": "❌ 無法從語句中擷取有效排程資訊"
            }

        try:
            response = requests.post("http://127.0.0.1:8000/mcp/calendar_scheduler", json=event)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "plugin": "calendar",
                    "title": event["title"],
                    "datetime": f"{event['date']} {event['time']}",
                    "message": f"✅ 已建立事件：{event['title']} 時間：{event['date']} {event['time']}"
                }
            else:
                return {
                    "status": "error",
                    "plugin": "calendar",
                    "message": "⚠️ 事件建立失敗",
                    "detail": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "plugin": "calendar",
                "message": "🚫 無法連線到日曆 API",
                "detail": str(e)
            }
