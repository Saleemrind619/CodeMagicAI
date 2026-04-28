import os
import re
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__, template_folder='../templates')

# API Setup
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def get_ai_response(prompt):
    try:
        # Simple and direct model call to avoid version errors
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Error: AI response is empty or blocked by safety filters."
    except Exception as e:
        # Agar 404 aaye to purana model try karega auto-healing ke liye
        if "404" in str(e):
            try:
                legacy_model = genai.GenerativeModel('gemini-pro')
                response = legacy_model.generate_content(prompt)
                return response.text
            except:
                return f"Error: Model not found. Check your API Key permissions."
        return f"Error: {str(e)}"

def detect_wp(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        theme = "Not Detected"
        theme_match = re.search(r'wp-content/themes/([^/]+)/', response.text)
        if theme_match:
            theme = theme_match.group(1).replace('-', ' ').title()
        plugins = set(re.findall(r'wp-content/plugins/([^/]+)/', response.text))
        plugin_list = [p.replace('-', ' ').title() for p in plugins]
        return {"status": "success", "theme": theme, "plugins": list(plugin_list)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text')
    editor = request.form.get('editor')
    
    if mode == 'wp_detect':
        return jsonify(detect_wp(user_text))

    result_text = get_ai_response(f"Expert Developer. Task: {mode}. Stack: {editor}. Input: {user_text}")
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

# Vercel handler
app_handler = app
