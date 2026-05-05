@app.route('/process', methods=['POST'])
def process():
    mode = request.form.get('mode')
    user_text = request.form.get('text', '').strip()
    
    # Default file name
    file_name = "index.html"

    if mode == 'wp_detect':
        if not user_text:
            return jsonify({"status": "error", "result": "URL missing"})
        result = deep_wp_check(user_text)
        return jsonify({
            "status": "success", 
            "result": result,
            "file_name": "detect_report.txt" # Detection ke liye file name
        })

    # AI Modes
    sys_msg = "Assistant mode."
    if mode == 'clone': 
        sys_msg = "Write complete single-file HTML code with Tailwind CSS."
        file_name = "cloned_site.html"
    elif mode == 'layout': 
        sys_msg = "Convert description to responsive HTML/CSS."
        file_name = "layout.html"
    elif mode == 'debug': 
        sys_msg = "Fix and return only corrected code."
        file_name = "fixed_code.txt"

    response = get_ai_response(user_text, sys_msg)
    
    # Yahan 'file_name' lazmi bhejni hai taake frontend download button dikhaye
    return jsonify({
        "status": "success", 
        "result": response,
        "file_name": file_name 
    })
