import os
import requests
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt, system_instruction):
    if not GROQ_KEY:
        return "Error: Groq API Key missing."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

def deep_wp_check(url):
    """Advanced detection logic to bypass basic security/hiding techniques"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Standard Request
        res = requests.get(url, headers=headers, timeout=12)
        html = res.text.lower()
        resp_headers = res.headers
        
        # 1. Check Standard Signs
        if any(x in html for x in ["wp-content", "wp-includes", "wp-json", "wp-block"]):
            return "✅ WordPress Detected (Standard Footprints)"

        # 2. Check Hidden REST API (Hard to hide)
        api_url = url.rstrip('/') + "/wp-json/wp/v2/"
        api_res = requests.get(api_url, headers=headers, timeout=5)
        if api_res.status_code == 200 and "namespaces" in api_res.text:
            return "✅ WordPress Detected (via REST API Fingerprinting)"

        # 3. Check Response Headers (Bypass front-end masks)
        link_header = resp_headers.get('Link', '')
        if 'api.w.org' in link_header or 'wp-json' in link_header:
            return "✅ WordPress Detected (via Header Analysis)"

        # 4. Check Common Hidden Files
        for file in ["/readme.html", "/license.txt"]:
            file_res = requests.get(url.rstrip('/') + file, headers=headers, timeout=5)
            if file_res.status_code == 200 and "wordpress" in file_res.text.lower():
                return f"✅ WordPress Detected (via {file} lookup)"

        return "❌ Not a WordPress Site (or High-Level Custom Masking)"

    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text', '').strip()
    
    # Default values
    file_name = "index.html"
    sys_msg = ""

    # WP DETECT MODE (Deep Scan)
    if mode == 'wp_detect':
        if not user_text:
            return jsonify({"status": "error", "result": "Please provide a URL."})
        
        url = user_text if user_text.startswith('http') else 'https://' + user_text
        detection_result = deep_wp_check(url)
        return jsonify({
            "status": "success", 
            "result": detection_result,
            "file_name": "detect_report.txt"
        })

    # AI MODES
    if mode == 'clone':
        sys_msg = "Write complete, single-file HTML code with Tailwind CSS to clone the aesthetic. Start directly with <!DOCTYPE html>."
        file_name = "cloned_site.html"
    elif mode == 'layout':
        sys_msg = "Convert this layout description to a professional, responsive HTML/CSS file using Tailwind."
        file_name = "layout.html"
    elif mode == 'debug':
        sys_msg = "Analyze and fix the following code. Return ONLY the corrected code."
        file_name = "fixed_code.txt"
    else:
        sys_msg = "You are a professional coding assistant."

    response = get_ai_response(user_text, sys_msg)
    
    return jsonify({
        "status": "success", 
        "result": response,
        "file_name": file_name
    })

app_handler = app
