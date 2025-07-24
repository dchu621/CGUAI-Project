class MCPAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def match(self, text: str) -> bool:
        raise NotImplementedError("match() 尚未實作")

    def run(self, text: str, context: dict = {}) -> str:
        raise NotImplementedError("run() 尚未實作")
