from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/summary", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    # TODO: Whisper + GPT 요약 처리 로직 연결
    return jsonify({
        "title": "예시 영상 제목",
        "summary": "이건 테스트 요약입니다.",
        "ingredients": ["재료1", "재료2"]
    })

