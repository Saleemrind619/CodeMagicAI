from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__, template_folder='../templates')

# --- WP Detection Function ---
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

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    return jsonify(detect_wp(data.get('url', '')))

@app.route('/ai-task', methods=['POST'])
def ai_task():
    data = request.json
    task_type = data.get('type') # clone, layout, or fix
    prompt = data.get('prompt', '')
    # AI logic connection placeholder
    result = f"Successfully processed {task_type} request for: {prompt[:50]}..."
    return jsonify({"status": "success", "result": result})

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
