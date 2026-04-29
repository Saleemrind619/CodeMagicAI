import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# Environment Variable se API Key lena
API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_ai_response(prompt):
    """
    Direct Google API call using requests. 
    Ye method sab se zyada stable hai Vercel aur Python ke liye.
    """
    if not API_KEY:
        return "Error: API Key missing in Vercel Environment Variables."

    # Stable v1 version aur Gemini 1.5 Flash model
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        res_data = response.json()
        
        if response.status_code == 200:
            # Sahi response milne par text extract karna
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Agar Google koi error bhejta hai (maslan Key block hai)
            error_msg = res_data.get('error', {}).get('message', 'Unknown Google API Error')
            return f"Error: Google says - {error_msg}"
            
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

def detect_wp(url):
    """WordPress Theme aur Plugins detect karne ka logic"""
    try:
        if not url.startswith('http'): 
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=12)
        
        theme = "Not Detected"
        theme_match = re.search(r'wp-content/themes/([^/]+)/', response.text)
        if theme_match:
            theme = theme_match.group(1).replace('-', ' ').title()
            
        plugins = set(re.findall(r'wp-content/plugins/([^/]+)/', response.text))
        plugin_list = [p.replace('-', ' ').title() for p in plugins]
        
        return {"status": "success", "theme": theme, "plugins": list(plugin_list)}
    except Exception as e:
        return {"status": "error", "message": f"Could not scan site: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text')
    editor = request.form.get('editor')
    
    # Mode check karna
    if mode == 'wp_detect':
        return jsonify(detect_wp(user_text))

    # AI Prompt taiyar karna
    full_prompt = f"Act as an expert web developer for {editor}. Task: {mode}. User Input: {user_text}. Please provide clean, professional code or advice."
    
    result_text = get_ai_response(full_prompt)
    
    if result_text.startswith("Error:"):
        return jsonify({"status": "error", "result": result_text})
    
    return jsonify({"status": "success", "result": result_text})

# Vercel handler
app_handler = app
