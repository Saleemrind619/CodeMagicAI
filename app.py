from flask import Flask, render_template, request, jsonify, send_file
from google import genai
from google.genai import types
import os
import shutil
import time

app = Flask(__name__)

# 1. API KEY YAHAN DALEIN
API_KEY = "AIzaSyA5ZT3pD6JP9TpFbE_YOLid28i4Fj5akO0"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview"

BASE_THEME_DIR = "generated_themes"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.form
        user_input = data.get('text', '')
        mode = data.get('mode', 'layout')
        editor = data.get('editor', 'elementor')
        
        # Strict English & Clean Format Prompt
        prompt = f"""
        Act as a Senior Web Developer. 
        Task: Generate a full professional package for: {user_input}
        Framework/Editor: {editor}
        
        STRICT RULES:
        1. All UI text, buttons, and content MUST be in English.
        2. Use format: ---FILE: filename.ext--- followed by code.
        3. No conversational text or introductions between files.
        4. If React/NextJS, include necessary folder structures in filenames.
        """

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MEDIUM"),
            )
        )
        
        ai_text = response.text
        timestamp = str(int(time.time()))
        theme_name = f"theme_{timestamp}"
        theme_path = os.path.join(BASE_THEME_DIR, theme_name)
        
        if not os.path.exists(theme_path):
            os.makedirs(theme_path)

        # Files saving logic with Error 123 fix
        files_data = ai_text.split("---FILE: ")
        for f_data in files_data:
            if "---" in f_data:
                parts = f_data.split("---")
                filename = parts[0].strip()
                content = parts[1].strip()
                
                # Check if it's a valid filename (contains dot and not too long)
                if "." in filename and len(filename) < 60:
                    file_full_path = os.path.join(theme_path, filename)
                    directory = os.path.dirname(file_full_path)
                    
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    
                    with open(file_full_path, "w", encoding="utf-8") as f:
                        f.write(content)

        # Create ZIP
        zip_name = f"{theme_name}.zip"
        shutil.make_archive(os.path.join(BASE_THEME_DIR, theme_name), 'zip', theme_path)

        return jsonify({
            "result": ai_text,
            "download_link": f"/download/{zip_name}"
        })
    
    except Exception as e:
        return jsonify({"result": f"System Error: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(BASE_THEME_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(BASE_THEME_DIR):
        os.makedirs(BASE_THEME_DIR)
    app.run(debug=True)