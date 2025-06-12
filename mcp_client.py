import socket

def send_mcp_command_tcp(command: str, host='localhost', port=4242) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(command.encode('utf-8') + b'\n')
            response = s.recv(4096)
            return response.decode('utf-8').strip()
    except Exception as e:
        print(f"⚠️ MCP TCP client error: {e}")
        return f"Error: {e}"
