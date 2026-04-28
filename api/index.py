import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__, template_folder='../templates')

# Environment Variable se Key uthana
API_KEY = os.environ.get("AIzaSyA5ZT3pD6JP9TpFbE_YOLid28i4Fj5akO0")
genai.configure(api_key=API_KEY)
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
        return {"status": "success", "theme": theme, "plugins": plugin_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai-task', methods=['POST'])
def ai_task():
    data = request.json
    task = data.get('type')
    prompt = data.get('prompt')
    try:
        response = model.generate_content(f"Act as an expert developer. Task: {task}. Input: {prompt}")
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/analyze-wp', methods=['POST'])
def analyze_wp():
    data = request.json
    return jsonify(detect_wp(data.get('url', '')))
