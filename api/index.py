import os
import requests
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt, system_instruction):
    if not GROQ_KEY:
        return "Error: Groq API Key missing."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text', '').strip()
    editor_content = request.form.get('editor', '')

    # Default file name
    file_name = "index.html"

    if mode == 'wp_detect':
        # (Purana WP Detect Logic yahan rahega...)
        try:
            url = user_text if user_text.startswith('http') else 'https://' + user_text
            res = requests.get(url, timeout=10)
            is_wp = "wp-content" in res.text
            return jsonify({"status": "success", "result": "✅ WordPress Detected" if is_wp else "❌ Not WP"})
        except: return jsonify({"status": "error", "result": "Connection Error"})

    if mode == 'clone':
        sys_msg = "Write complete, single-file HTML code with Tailwind CSS. Start directly with <!DOCTYPE html>."
        file_name = "cloned_site.html"
    elif mode == 'layout':
        sys_msg = "Convert this layout to a single-file responsive HTML/CSS."
        file_name = "layout.html"
    elif mode == 'debug':
        sys_msg = "Fix the code and return ONLY the corrected code."
        file_name = "fixed_code.txt"
    else:
        sys_msg = "Assistant mode."

    response = get_ai_response(user_text, sys_msg)
    
    return jsonify({
        "status": "success", 
        "result": response,
        "file_name": file_name # Frontend ko file name bhej rahe hain
    })

app_handler = app
