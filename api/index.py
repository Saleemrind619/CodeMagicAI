import os
import requests
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION ---
# Humne key code se nikal di hai, ab ye Vercel ki settings se uthayega
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Groq Client Initialize
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt):
    if not GROQ_KEY:
        return "Error: Groq API Key missing in Vercel Settings."

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert developer."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Groq API Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text')
    editor = request.form.get('editor')

    if not user_text:
        return jsonify({"status": "error", "result": "Input is empty!"})

    # AI Generation
    prompt = f"Task: {mode}. Editor: {editor}. Request: {user_text}"
    response = get_ai_response(prompt)
    
    return jsonify({"status": "success", "result": response})

app_handler = app
