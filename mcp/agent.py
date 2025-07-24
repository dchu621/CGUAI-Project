from mcp.base import MCPAgent
from mcp.plugins.calendar import CalendarPlugin
# 如果日後有更多 plugin，這裡繼續加

class MCPController:
    def __init__(self):
        self.plugins = [
            CalendarPlugin(),
            # 之後可以繼續加像 WeatherPlugin(), NotePlugin()...
        ]

    def dispatch(self, text: str, context: dict = {}) -> dict:
        for plugin in self.plugins:
            if plugin.match(text):
                return plugin.run(text, context)
        
        return {
            "status": "none",
            "message": "🤖 沒有找到符合的指令，請再描述清楚一些～"
        }
