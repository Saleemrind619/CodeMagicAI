import os
import requests
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION ---
# Key Vercel ki settings (Environment Variables) se uthayega
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Groq Client Initialize
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt):
    if not GROQ_KEY:
        return "Error: Groq API Key missing in Vercel Settings."

    try:
        # Naya Model: llama-3.3-70b-versatile
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert full-stack developer. Provide clean, professional code solutions."},
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
    user_text = request.form.get('text')
    editor = request.form.get('editor')

    if not user_text:
        return jsonify({"status": "error", "result": "Input is empty!"})

    # --- WordPress Detection Logic ---
    if mode == 'wp_detect':
        try:
            target = user_text if user_text.startswith('http') else 'https://' + user_text
            res = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            theme = re.search(r'wp-content/themes/([^/]+)/', res.text)
            theme_name = theme.group(1).title() if theme else "Custom/Unknown"
            is_wp = "wp-content" in res.text or "wp-includes" in res.text
            
            if is_wp:
                return jsonify({"status": "success", "result": f"✅ WordPress Site Detected!\n🎨 Theme: {theme_name}"})
            else:
                return jsonify({"status": "success", "result": "❌ Not a WordPress site."})
        except Exception as e:
            return jsonify({"status": "error", "result": f"Scan failed: {str(e)}"})

    # --- AI Generation (Clone, Layout, Debug) ---
    prompt = f"Mode: {mode}. Editor: {editor}. Request: {user_text}"
    response = get_ai_response(prompt)
    
    if "Error" in response:
        return jsonify({"status": "error", "result": response})
        
    return jsonify({"status": "success", "result": response})

app_handler = app
