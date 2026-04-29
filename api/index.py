import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# Vercel Environment Variable
API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_ai_response(prompt):
    if not API_KEY:
        return "Error: API Key missing in Vercel settings."

    # NAYA RASTA: Sab se stable model 'gemini-pro' jo har key par chalta hai
    # Version 'v1' ke sath stable connection
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        # Timeout barha diya hai taake response lazmi aaye
        response = requests.post(url, headers=headers, json=payload, timeout=40)
        res_data = response.json()
        
        if response.status_code == 200:
            if 'candidates' in res_data:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Error: AI responded but no content was found."
        else:
            # Agar ab bhi error aaye, to humein sahi wajah pata chal jayegi
            msg = res_data.get('error', {}).get('message', 'Unknown Connection Error')
            return f"Error: Google API says - {msg}"
            
    except Exception as e:
        return f"System Error: {str(e)}"

def detect_wp(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
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
        res = detect_wp(user_text)
        if res["status"] == "success":
            output = f"WP Theme: {res['theme']}\nPlugins Found: " + (", ".join(res['plugins']) if res['plugins'] else "None")
            return jsonify({"status": "success", "result": output})
        return jsonify({"status": "error", "result": res["message"]})

    # AI Prompt Formatting
    full_prompt = f"Role: Expert Developer. Mode: {mode}. Stack: {editor}. Task: {user_text}"
    result_text = get_ai_response(full_prompt)
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

app_handler = app
