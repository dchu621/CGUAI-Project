from mcp.agent import MCPController

if __name__ == "__main__":
    controller = MCPController()
    print("🧠 MCP 啟動：請輸入自然語句（可包含排程指令）...")

    while True:
        text = input("💬 你說：")
        result = controller.dispatch(text)
        print(f"📢 回應：{result['message']}")
