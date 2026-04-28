import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# API Configuration
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text')
    editor = request.form.get('editor')
    
    try:
        # Forcefully using gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Task: {mode}, Platform: {editor}, Input: {user_text}"
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            return jsonify({"status": "success", "result": response.text})
        else:
            return jsonify({"status": "error", "result": "AI Safety Triggered."})
            
    except Exception as e:
        # Agar ab bhi error aaye to ye message batayega exactly kya masla hai
        return jsonify({"status": "error", "result": f"System Alert: {str(e)}"})
