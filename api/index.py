import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# Vercel key check
API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_ai_response(prompt):
    if not API_KEY:
        return "Error: API Key is missing in Vercel. Please check Environment Variables."

    # Hum pehle Flash try karenge, phir Pro. Taake error na aaye.
    models_to_try = [
        "gemini-1.5-flash", 
        "gemini-pro"
    ]
    
    last_error = ""
    for model in models_to_try:
        # 'v1beta' naye accounts aur free tier ke liye zyada stable hai
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            res_data = response.json()
            
            if response.status_code == 200:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                last_error = res_data.get('error', {}).get('message', 'Unknown Error')
                continue # Agar ye model fail ho to agla try karo
        except Exception as e:
            last_error = str(e)
            continue

    return f"Error: Google API is not accepting the request. Message: {last_error}"

def detect_wp(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=12)
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
            output = f"WP Theme: {res['theme']}\nPlugins: " + (", ".join(res['plugins']) if res['plugins'] else "None")
            return jsonify({"status": "success", "result": output})
        return jsonify({"status": "error", "result": res["message"]})

    full_prompt = f"Expert Web Dev Mode. Context: {mode} for {editor}. Task: {user_text}"
    result_text = get_ai_response(full_prompt)
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

app_handler = app
