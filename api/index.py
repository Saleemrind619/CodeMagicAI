import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# Environment Variable se API Key
API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_ai_response(prompt):
    if not API_KEY:
        return "Error: API Key missing in Vercel settings."

    # Hum yahan 'v1beta' use kar rahe hain kyunke Gemini 1.5 Flash wahan behtar chalta hai
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        
        if response.status_code == 200:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Deep error check
            error_info = res_data.get('error', {})
            msg = error_info.get('message', 'Unknown Error')
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
        return {"status": "success", "theme": theme, "plugins": list(plugins)}
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
            output = f"Theme: {res['theme']}\nPlugins: " + ", ".join(res['plugins'])
            return jsonify({"status": "success", "result": output})
        return jsonify({"status": "error", "result": res["message"]})

    full_prompt = f"Expert Web Dev Mode: {mode}. Editor: {editor}. Request: {user_text}"
    result_text = get_ai_response(full_prompt)
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

app_handler = app
