import os  
import requests  
from flask import Flask, render_template, request, jsonify  
from groq import Groq  
  
app = Flask(__name__, template_folder='../templates')  
  
# Environment Variable for Groq  
GROQ_KEY = os.environ.get("GROQ_API_KEY")  
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None  
  
def get_ai_response(prompt, system_instruction):  
    if not client:  
        return "Error: Groq API Key missing in Environment Variables."  
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
    """Ultra-Aggressive detection logic to bypass high-level masking"""  
    headers = {  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',  
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',  
    }  
      
    try:  
        if not url.startswith('http'):  
            url = 'https://' + url  
              
        # Step 1: Base Request  
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)  
        html = res.text.lower()  
          
        # WP Indicators  
        wp_indicators = ["wp-content", "wp-includes", "wp-json", "wp-block", "wp-embed", "rel='https://api.w.org/'"]  
        if any(x in html for x in wp_indicators):  
            return "✅ WordPress Detected (Source Analysis)"  
  
        # Step 2: REST API Bypass Check  
        api_endpoints = ["/wp-json/wp/v2/", "/index.php?rest_route=/", "/?rest_route=/"]  
        for endpoint in api_endpoints:  
            try:  
                api_res = requests.get(url.rstrip('/') + endpoint, headers=headers, timeout=5)  
                if api_res.status_code == 200 and "namespaces" in api_res.text:  
                    return "✅ WordPress Detected (via REST API Bypass)"  
            except: continue  
  
        # Step 3: Admin Path Check  
        try:  
            admin_check = requests.get(url.rstrip('/') + "/wp-login.php", headers=headers, timeout=5)  
            if admin_check.status_code == 200 and "user_login" in admin_check.text:  
                return "✅ WordPress Detected (Admin Path Unmasked)"  
        except: pass  
  
        return "❌ Not a WordPress Site"  
    except Exception as e:  
        return f"⚠️ Scan Failed: {str(e)}"  
  
@app.route('/')  
def home():  
    return render_template('index.html')  
  
@app.route('/process', methods=['POST'])  
def process():  
    mode = request.form.get('mode')  
    user_text = request.form.get('text', '').strip()  
  
    if mode == 'wp_detect':  
        if not user_text:  
            return jsonify({"status": "error", "result": "URL missing"})  
        result = deep_wp_check(user_text)  
        return jsonify({"status": "success", "result": result})  
  
    # AI Modes  
    sys_msg = "Assistant mode."  
    if mode == 'clone': sys_msg = "Write complete single-file HTML code with Tailwind CSS."  
    elif mode == 'layout': sys_msg = "Convert description to responsive HTML/CSS."  
    elif mode == 'debug': sys_msg = "Fix and return only corrected code."  
  
    response = get_ai_response(user_text, sys_msg)  
    return jsonify({"status": "success", "result": response})  
  
# Critical for Vercel/Serverless  
app_handler = app
