from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__, template_folder='../templates')

def detect_wp_data(url):
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Theme Detection
        theme_name = "Not Detected"
        theme_match = re.search(r'wp-content/themes/([^/]+)/', response.text)
        if theme_match:
            theme_name = theme_match.group(1).replace('-', ' ').title()

        # Plugin Detection
        plugins = set()
        plugin_matches = re.findall(r'wp-content/plugins/([^/]+)/', response.text)
        for p in plugin_matches:
            plugins.add(p.replace('-', ' ').title())
            
        return {
            "status": "success",
            "theme": theme_name,
            "plugins": list(plugins) if plugins else ["No plugins found or Site is not WordPress"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    target_url = data.get('url', '')
    result = detect_wp_data(target_url)
    return jsonify(result)

# Vercel focus
