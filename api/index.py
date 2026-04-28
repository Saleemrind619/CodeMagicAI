import os
import re
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__, template_folder='../templates')

# Google API Configuration
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Use the most stable model name
# 'gemini-1.5-flash' automatically points to the latest supported version
model = genai.GenerativeModel('gemini-1.5-flash')

def detect_wp(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        theme = "Not Detected"
        theme_match = re.search(r'wp-content/themes/([^/]+)/', response.text)
        if theme_match: theme = theme_match.group(1).replace('-', ' ').title()
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
        # Prompt build up
        prompt = f"Role: Expert Developer. Task: {mode}. Platform: {editor}. Input: {user_text}"
        
        # Fixing the generation call
        response = model.generate_content(prompt)
        
        # Verify if response has text property
        if response and hasattr(response, 'text'):
            return jsonify({"status": "success", "result": response.text})
        else:
            return jsonify({"status": "error", "result": "AI Safety filter blocked the output or empty response."})
            
    except Exception as e:
        # Return the actual error for debugging
        return jsonify({"status": "error", "result": f"System Alert: {str(e)}"})
