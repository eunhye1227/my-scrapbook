from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import openai
import whisper
import yt_dlp
import uuid
from pytube import YouTube

load_dotenv()

app = Flask(__name__)

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

if USE_GPT and API_KEY:
    openai.api_key = API_KEY
else:
    print("🛡️ GPT 호출은 비활성화됨. 가난이 너를 지켜준다.")

# 🎯 설명란 가져오기
def get_video_description(youtube_url):
    try:
        yt = YouTube(youtube_url)
        return yt.description
    except Exception as e:
        print(f"[설명란 가져오기 실패] {e}")
        return ""

# 🎯 오디오 다운로드
def download_audio(youtube_url):
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return filename

# 🎯 Whisper 자막 추출
def transcribe_audio(file_path):
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(file_path)
    return result["text"]

@app.route("/summary", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    used_description = False
    transcript = ""

    try:
        description = get_video_description(youtube_url)
        if description and len(description.strip()) > 50:
            transcript = description
            used_description = True
        else:
            audio_path = download_audio(youtube_url)
            transcript = transcribe_audio(audio_path)
            os.remove(audio_path)
    except Exception as e:
        return jsonify({"error": "자막 또는 설명 추출 실패", "details": str(e)}), 500

    summary = "GPT 호출 안 함 (USE_GPT=false 설정됨)"
    if USE_GPT and API_KEY:
        try:
            source_label = "영상 설명란" if used_description else "음성 자막"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 요리 영상을 요약하는 요약가입니다."},
                    {"role": "user", "content": f"{source_label}을 기반으로 요약해줘:\n\n{transcript}"}
                ],
                temperature=0.7
            )
            summary = response.choices[0].message["content"].strip()
        except Exception as e:
            return jsonify({"error": "GPT 호출 실패", "details": str(e)}), 500

    return jsonify({
        "title": "요약된 영상",
        "summary": summary,
        "ingredients": ["재료1", "재료2"],
        "source": "description" if used_description else "whisper"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
