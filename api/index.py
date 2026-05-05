import os  
import requests  
from flask import Flask, render_template, request, jsonify  
from groq import Groq  
  
app = Flask(__name__, template_folder='../templates')  
  
# Environment Variable
GROQ_KEY = os.environ.get("GROQ_API_KEY")  
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None  
  
def get_ai_response(prompt, system_instruction):  
    if not client: return "Error: Groq API Key missing."  
    try:  
        chat_completion = client.chat.completions.create(  
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],  
            model="llama-3.3-70b-versatile",  
            temperature=0.6,  
        )  
        return chat_completion.choices[0].message.content  
    except Exception as e: return f"System Error: {str(e)}"  
  
def deep_wp_check(url):  
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}  
    try:  
        if not url.startswith('http'): url = 'https://' + url  
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)  
        html = res.text.lower()  
        if any(x in html for x in ["wp-content", "wp-includes", "wp-json", "ver=wp-"]): return "✅ WordPress Detected"  
        api_res = requests.get(url.rstrip('/') + "/wp-json/wp/v2/", headers=headers, timeout=5)  
        if api_res.status_code == 200: return "✅ WordPress Detected (API Leak)"  
        return "❌ Not a WordPress Site"  
    except: return "⚠️ Scan Failed"  
  
@app.route('/')  
def home(): return render_template('index.html')  
  
@app.route('/process', methods=['POST'])  
def process():  
    mode = request.form.get('mode')  
    user_text = request.form.get('text', '').strip()  
    file_name = "index.html"  
  
    if mode == 'wp_detect':  
        result = deep_wp_check(user_text)  
        return jsonify({"status": "success", "result": result, "file_name": "report.txt"})  
  
    if mode == 'clone':  
        sys_msg = "Generate full HTML with Tailwind CSS. Output code ONLY."  
        file_name = "cloned_page.html"  
    elif mode == 'layout':  
        sys_msg = "Convert description to responsive Tailwind HTML code."  
        file_name = "layout.html"  
    elif mode == 'debug':  
        sys_msg = "Fix bugs and return ONLY corrected code."  
        file_name = "fixed_code.txt"  
    else: sys_msg = "Assistant mode."  
  
    response = get_ai_response(user_text, sys_msg)  
    return jsonify({"status": "success", "result": response, "file_name": file_name})  
  
app_handler = app
