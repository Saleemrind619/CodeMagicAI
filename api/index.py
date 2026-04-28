import os
import re
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__, template_folder='../templates')

# Vercel Settings se API Key lena
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Latest Stable Model Name
model = genai.GenerativeModel('gemini-1.5-flash')

def detect_wp(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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
        prompt = f"Expert Developer Mode. Task: {mode}. Platform: {editor}. Input: {user_text}"
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "result": f"AI Error: {str(e)}"})

# Vercel handles the app object
