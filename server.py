from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mcp_client import send_mcp_command_tcp
import subprocess, tempfile, whisper, requests, uuid, asyncio, os

# ---------------- Config ----------------
OLLAMA_HOST     = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
PRIMARY_ENDPOINT = f"{OLLAMA_HOST}/api/generate"
DEFAULT_MODEL    = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")

# 暫存每場會議的文字片段
store: dict[str, list[str]] = {}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/web", StaticFiles(directory="frontend", html=True), name="frontend")

def call_ollama_for_actions(text: str) -> list[str]:
    prompt = (
        "You are an AI agent. Read this meeting fragment.\n"
        "If it contains executable commands (e.g. turn_on_light), output a Python list of strings;\n"
        "otherwise output [].\n\nFragment:\n" + text
    )
    r = requests.post(PRIMARY_ENDPOINT, json={
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    })
    r.raise_for_status()
    return eval(r.json()["response"].strip())

def call_ollama_for_summary(text: str) -> str:
    prompt = "請將以下完整會議內容做條列式重點摘要與代辦事項：\n" + text
    r = requests.post(PRIMARY_ENDPOINT, json={
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    })
    r.raise_for_status()
    return r.json()["response"].strip()

async def send_to_mcp(action: str):
    try:
        mcp_command = f"mcp:action {action}"
        result = await asyncio.to_thread(send_mcp_command_tcp, mcp_command)
        print(f"✅ MCP response: {result}")
    except Exception as e:
        print(f"⚠️ MCP action failed ({action}): {e}")

@app.post("/begin_meeting")
def begin_meeting():
    mid = str(uuid.uuid4())
    store[mid] = []
    return {"meeting_id": mid}

@app.post("/chunk")
async def chunk(
    meeting_id: str = Form(...),
    file      : UploadFile = File(...)
):
    # 1) 儲存前端傳來的 WAV
    suffix = os.path.splitext(file.filename)[1].lower() or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(await file.read())
        in_path = f.name

    # 2) 如果不是 WAV，轉成 16k mono WAV；若已是 WAV，直接用
    if suffix != ".wav":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f2:
            wav_path = f2.name
        cmd = ["ffmpeg", "-y", "-i", in_path, "-ac", "1", "-ar", "16000", "-f", "wav", wav_path]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print("❌ ffmpeg error:", e.stderr.decode())
            raise HTTPException(500, "ffmpeg 轉檔失敗")
    else:
        wav_path = in_path

    # 3) Whisper 轉文字
    try:
        model  = whisper.load_model("base")
        result = model.transcribe(wav_path)
        text   = result["text"].strip()
    except Exception as e:
        raise HTTPException(500, f"Whisper 轉譯失敗: {e}")

    # 暫存文字片段
    store[meeting_id].append(text)

    # 4) 呼叫 Ollama 抽出即時指令，並丟給 MCP
    actions = call_ollama_for_actions(text)
    for act in actions:
        asyncio.create_task(send_to_mcp(act))

    return {"transcript": text, "actions": actions}

@app.get("/end_meeting")
def end_meeting(meeting_id: str):
    if meeting_id not in store:
        raise HTTPException(404, "meeting_id not found")
    full_text = "\n".join(store.pop(meeting_id))
    summary   = call_ollama_for_summary(full_text)
    return {"summary": summary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
