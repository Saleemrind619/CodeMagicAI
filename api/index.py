import os
import requests
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION ---
# Agar Vercel se key nahi mil rahi, to aap yahan apni key ' ' ke darmiyan paste kar sakte hain (sirf testing ke liye)
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyDL3vAeHHhwdwf-Sgj5kGNRNNbZiyxsDCY")

def get_ai_response(prompt):
    if not API_KEY or "YAHAN_" in API_KEY:
        return "Error: API Key is missing. Please check Vercel Environment Variables."

    # Direct API Call - Sab se stable rasta
    # Hum 'gemini-pro' use kar rahe hain kyunke ye har region aur har key par chalta hai
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Google jo error bhej raha hai wahi dikhayen
            err = data.get('error', {}).get('message', 'Unknown Google Error')
            return f"Google API Error: {err}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text')
    editor = request.form.get('editor')

    # WordPress Detection Logic
    if mode == 'wp_detect':
        try:
            target = user_text if user_text.startswith('http') else 'https://' + user_text
            res = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            theme = re.search(r'wp-content/themes/([^/]+)/', res.text)
            theme_name = theme.group(1).title() if theme else "Unknown"
            return jsonify({"status": "success", "result": f"WordPress Site Detected!\nTheme: {theme_name}"})
        except:
            return jsonify({"status": "error", "result": "Could not scan the website."})

    # AI Generation
    prompt = f"System: You are an expert dev. Task: {mode}. Editor: {editor}. User Request: {user_text}"
    response = get_ai_response(prompt)
    
    if "Error" in response:
        return jsonify({"status": "error", "result": response})
    return jsonify({"status": "success", "result": response})

app_handler = app
