import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import whisper
import requests

# 參數設定
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FILE = "audio.wav"
TEXT_FILE = "audio.txt"
WHISPER_MODEL = "base"    # 或 small, medium, large
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"  # 根據你的 Ollama Server API 路徑

def record_until_enter():
    """Press Enter to start & stop recording, return numpy array of audio."""
    print("按 Enter 開始錄音")
    input()
    print("錄音中...再按 Enter 停止")
    frames = []

    def callback(indata, frames_count, time, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype='int16',
                        callback=callback):
        input()  # 等使用者再按一次 Enter
    audio = np.concatenate(frames, axis=0)
    return audio

def save_wav(audio, filename):
    write(filename, SAMPLE_RATE, audio)
    print(f"已儲存錄音檔：{filename}")

def transcribe_with_whisper(audio_path, model_name):
    print("呼叫 Whisper 轉文字...")
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    text = result["text"].strip()
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"已儲存文字檔：{TEXT_FILE}")
    return text

def send_to_ollama(prompt_text):
    print("送出到 FastAPI 伺服器，請稍候...")
    payload = {
        "transcript": prompt_text,
        "model": "mistral:7b-instruct",
        "system_prompt": "你是會議摘要助理，請整理會議重點與代辦事項"
    }
    resp = requests.post("http://localhost:8000/process_whisper", json=payload)
    resp.raise_for_status()
    return resp.json()["summary"]

def main():
    audio = record_until_enter()
    save_wav(audio, AUDIO_FILE)
    text = transcribe_with_whisper(AUDIO_FILE, WHISPER_MODEL)
    print("── 轉錄文字 ──")
    print(text)
    print("── Ollama 回覆 ──")
    answer = send_to_ollama(text)
    print(answer)

if __name__ == "__main__":
    main()
