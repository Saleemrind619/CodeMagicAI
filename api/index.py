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
              
        # Step 1: Base Request with redirects allowed  
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)  
        html = res.text.lower()  
          
        # 1. Triple-Check HTML (Hidden Comments, Tags & Meta)  
        wp_indicators = [
            "wp-content", "wp-includes", "wp-json", "wp-block", "wp-embed",
            "rel='https://api.w.org/'", "s0.wp.com", "rvm-wp", "ver=wp-",
            "wp-emoji-release.min.js"
        ]  
        if any(x in html for x in wp_indicators):  
            return "✅ WordPress Detected (Source Analysis)"  
  
        # 2. Aggressive API Scrutiny (The 'Unmasker' Check)  
        api_endpoints = ["/wp-json/wp/v2/", "/index.php?rest_route=/", "/?rest_route=/", "/wp-json/"]  
        for endpoint in api_endpoints:  
            try:  
                api_res = requests.get(url.rstrip('/') + endpoint, headers=headers, timeout=5)  
                if api_res.status_code == 200 and ("namespaces" in api_res.text or "routes" in api_res.text):  
                    return "✅ WordPress Detected (via REST API Bypass)"  
            except: continue  
  
        # 3. Asset & Header Deep Scan  
        if 'wordpress_test_cookie' in str(res.cookies) or 'wp-settings' in str(res.cookies):  
            return "✅ WordPress Detected (Cookie Analysis)"  
            
        if 'wp-json' in res.headers.get('Link', ''):  
            return "✅ WordPress Detected (Header Link Scan)"  
  
        # 4. CSS Class & Structural Detection  
        css_classes = ["wp-post-image", "attachment-post-thumbnail", "body.wp-custom-logo", "has-blocks"]  
        if any(cls in html for cls in css_classes):  
            return "✅ WordPress Detected (CSS Layout Pattern)"  
  
        # 5. Default Admin Paths  
        try:  
            admin_check = requests.get(url.rstrip('/') + "/wp-login.php", headers=headers, timeout=5)  
            if admin_check.status_code == 200 and "user_login" in admin_check.text:  
                return "✅ WordPress Detected (Admin Path Found)"  
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
    
    # Default file name settings for download
    file_name = "index.html"  
  
    if mode == 'wp_detect':  
        if not user_text:  
            return jsonify({"status": "error", "result": "Please enter a URL"})  
        result = deep_wp_check(user_text)  
        return jsonify({
            "status": "success", 
            "result": result,
            "file_name": "detect_report.txt"
        })  
  
    # AI Modes configuration
    if mode == 'clone':  
        sys_msg = "Write complete, single-file HTML code with Tailwind CSS. Start directly with <!DOCTYPE html>."  
        file_name = "cloned_site.html"  
    elif mode == 'layout':  
        sys_msg = "Convert this layout to a single-file responsive HTML/CSS."  
        file_name = "layout.html"  
    elif mode == 'debug':  
        sys_msg = "Fix the code and return ONLY the corrected code."  
        file_name = "fixed_code.txt"  
    else:  
        sys_msg = "Assistant mode."  
  
    response = get_ai_response(user_text, sys_msg)  
      
    return jsonify({  
        "status": "success",   
        "result": response,  
        "file_name": file_name  
    })  
  
# Critical for Vercel/Serverless deployment  
app_handler = app
