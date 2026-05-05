import os
import requests
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION ---
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt):
    if not GROQ_KEY:
        return "Error: Groq API Key missing in Vercel Settings."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert full-stack developer."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=4096,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Groq API Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text').strip()
    editor = request.form.get('editor')

    if not user_text:
        return jsonify({"status": "error", "result": "Input is empty!"})

    # --- ENHANCED WordPress Detection Logic ---
    if mode == 'wp_detect':
        try:
            target = user_text if user_text.startswith('http') else 'https://' + user_text
            # User-Agent add kiya hai taake website request block na kare
            res = requests.get(target, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            content = res.text.lower()
            
            # Multiple Checks for WordPress
            is_wp = any(x in content for x in ["wp-content", "wp-includes", "wp-json", "wp-login", "xmlrpc.php"])
            
            if is_wp:
                # Theme nikalne ka behtar tareeka
                theme_match = re.search(r'wp-content/themes/([^/|\"|\']+)', res.text)
                theme_name = theme_match.group(1).replace('-', ' ').title() if theme_match else "Custom or Hidden Theme"
                
                return jsonify({
                    "status": "success", 
                    "result": f"✅ WordPress Site Detected!\n🎨 Theme: {theme_name}\n🔍 Status: Verified by CodeMagic"
                })
            else:
                return jsonify({"status": "success", "result": "❌ Not a WordPress site or security is blocking the scan."})
        except Exception as e:
            return jsonify({"status": "error", "result": f"Scan failed: Site might be down or blocking requests. ({str(e)})"})

    # --- AI Generation ---
    prompt = f"Mode: {mode}. Request: {user_text}"
    response = get_ai_response(prompt)
    
    return jsonify({"status": "success", "result": response})

app_handler = app
