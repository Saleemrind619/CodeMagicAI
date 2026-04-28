import os
import re
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.generativeai.types import RequestOptions

app = Flask(__name__, template_folder='../templates')

# Google API Setup
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def get_ai_response(prompt):
    """Self-healing model caller that tries different versions if 404 occurs"""
    # Version list to try
    versions = ["v1", "v1beta"]
    
    for ver in versions:
        try:
            # Force the specific API version to bypass 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                request_options=RequestOptions(api_version=ver)
            )
            return response.text
        except Exception as e:
            if "404" in str(e) and ver == "v1":
                continue # Try next version if v1 fails
            return f"Error: {str(e)}"
    return "Could not connect to any model version."

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

    try:
        prompt = f"Role: Expert Developer. Mode: {mode}. Stack: {editor}. Input: {user_text}"
        result_text = get_ai_response(prompt)
        
        if "Error:" in result_text:
            return jsonify({"status": "error", "result": result_text})
        
        return jsonify({"status": "success", "result": result_text})
            
    except Exception as e:
        return jsonify({"status": "error", "result": f"System Crash: {str(e)}"})

# Vercel handler
app_handler = app
