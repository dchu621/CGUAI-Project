# fake_mcp_server.py
import socket

HOST = '0.0.0.0'
PORT = 4242

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"🟢 MCP server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"📥 Connected by {addr}")
            data = conn.recv(1024).decode('utf-8').strip()
            print(f"📨 Received MCP command: {data}")
            conn.sendall(f"✅ MCP executed: {data}".encode('utf-8'))
