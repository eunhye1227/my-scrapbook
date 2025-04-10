from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

# OpenAI 클라이언트 설정
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/summary", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    # Whisper 자막 추출 자리 (지금은 임시 텍스트)
    transcript = "이건 예시 자막입니다. 실제로는 whisper로 추출한 텍스트가 여기에 들어갑니다."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 요리 영상을 요약하는 요약가입니다."},
                {"role": "user", "content": f"다음 자막을 요약해줘:\n\n{transcript}"}
            ],
            temperature=0.7
        )

        summary = response.choices[0].message.content.strip()

    except Exception as e:
        return jsonify({"error": "GPT 호출 실패", "details": str(e)}), 500

    return jsonify({
        "title": "예시 영상 제목",
        "summary": summary,
        "ingredients": ["재료1", "재료2"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
