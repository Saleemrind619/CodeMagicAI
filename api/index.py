import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_ai_response(prompt):
    # Try multiple combinations of versions and models until one works
    # Yeh list is liye hai ke agar aik fail ho to doosra chale
    endpoints = [
        ("v1", "gemini-1.5-flash"),
        ("v1beta", "gemini-1.5-flash"),
        ("v1", "gemini-pro")
    ]
    
    last_error = ""
    
    for version, model in endpoints:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            res_data = response.json()
            
            if response.status_code == 200:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                last_error = res_data.get('error', {}).get('message', 'Unknown Error')
                continue # Try next combination if this one fails
        except Exception as e:
            last_error = str(e)
            continue

    return f"Error: System tried all versions. Google says: {last_error}"

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

    full_prompt = f"Act as an expert developer for {editor}. Task: {mode}. Input: {user_text}"
    result_text = get_ai_response(full_prompt)
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

app_handler = app
