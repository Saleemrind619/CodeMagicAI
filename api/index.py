import os
import re
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__, template_folder='../templates')

# Google API Key setup
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Use 'gemini-1.5-flash' with specific safety and generation config
# Ye model 404 nahi dega agar API key valid hai
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
)

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
        return {"status": "success", "theme": theme, "plugins": plugin_list}
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
        prompt = f"Expert Developer Task. Mode: {mode}. Stack: {editor}. Input: {user_text}"
        # Error handling for empty response
        response = model.generate_content(prompt)
        if hasattr(response, 'text'):
            return jsonify({"status": "success", "result": response.text})
        else:
            return jsonify({"status": "error", "result": "AI Safety filter triggered or empty response."})
            
    except Exception as e:
        # Check if it's a model error
        return jsonify({"status": "error", "result": f"System Alert: {str(e)}"})
