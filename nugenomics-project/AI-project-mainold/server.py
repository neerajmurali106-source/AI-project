import os
import traceback
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio

import google.generativeai as genai
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "nugenomics-project"))
from my_agent.agent import root_agent


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
print("🔑 Loaded API key:", os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__, static_folder="web/static", template_folder="web")
CORS(app)

APP_NAME = "MultiAgentApp"
USER_ID = "web_user"
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    session_service=session_service,
    app_name=APP_NAME
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat(): 
    try:
        data = request.get_json()
        query = data.get("message", "").strip()

        if not query:
            return jsonify({"reply": "Please enter a valid question."}), 400

        session_id = "main_session"

        async def get_response():

            await session_service.delete_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
            await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

            full_response = ""

            content = types.Content(role="user", parts=[types.Part(text=query)])

            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=content
            ):
                if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            full_response += part.text

                if hasattr(event, "is_final_response") and event.is_final_response():
                    break

            return full_response if full_response else "No response received."

        response = asyncio.run(get_response())
        return jsonify({"reply": response})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {type(e).__name__} - {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
