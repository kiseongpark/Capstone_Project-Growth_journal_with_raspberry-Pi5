# tts_utils.py
import re
import subprocess
from gtts import gTTS

def extract_summary(text: str) -> str:
    """
    Gemini 응답에서 '마지막 한 줄 요약'을 뽑아냅니다.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    summary = lines[-1]
    summary = re.sub(r'^\s*(요약\s*[:\-]\s*|Summary\s*[:\-]\s*)', '', summary, flags=re.I)
    return summary[:120]

def speak_ko(summary_text: str, mp3_path: str = "summary_tts.mp3"):
    """
    gTTS로 한국어 음성 생성 후 mpg123로 재생합니다.
    """
    if not summary_text:
        print("[TTS] 빈 텍스트라 음성을 재생하지 않습니다.")
        return
    try:
        tts = gTTS(summary_text, lang='ko', slow=False)
        tts.save(mp3_path)
        print(f"[TTS] MP3 저장: {mp3_path}")
        subprocess.run(["mpg123", "-q", mp3_path], check=True)
        print("[TTS] 재생 완료")
    except Exception as e:
        print(f"[TTS 오류] {e}")
