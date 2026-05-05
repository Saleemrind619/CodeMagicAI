<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Magical AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .gradient-text { background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="bg-[#0f172a] min-h-screen text-white flex flex-col items-center p-4">

    <h1 class="text-4xl font-black mb-8 gradient-text mt-10">CODE MAGICAL AI</h1>

    <!-- Action Buttons -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mb-8">
        <button onclick="setMode('clone')" class="glass p-4 rounded-xl hover:bg-blue-600 transition">🚀 Clone Website</button>
        <button onclick="setMode('layout')" class="glass p-4 rounded-xl hover:bg-purple-600 transition">🎨 Layout to Code</button>
        <button onclick="setMode('debug')" class="glass p-4 rounded-xl hover:bg-red-600 transition">🔍 Fix My Bug</button>
        <button onclick="setMode('wp_detect')" class="glass p-4 rounded-xl hover:bg-green-600 transition">🕵️ WP Detect</button>
    </div>

    <!-- PIYARI LOOK OPTIONS (New Section) -->
    <div class="w-full max-w-4xl grid grid-cols-3 gap-4 mb-10">
        <div class="glass p-4 rounded-2xl text-center border-b-4 border-pink-500">
            <i class="fas fa-cubes text-pink-500 text-2xl mb-2"></i>
            <h4 class="font-bold text-xs uppercase tracking-widest">Elementor</h4>
            <p class="text-[10px] text-gray-400">Ready to Use</p>
        </div>
        <div class="glass p-4 rounded-2xl text-center border-b-4 border-cyan-400">
            <i class="fab fa-css3-alt text-cyan-400 text-2xl mb-2"></i>
            <h4 class="font-bold text-xs uppercase tracking-widest">Tailwind CSS</h4>
            <p class="text-[10px] text-gray-400">Modern Styling</p>
        </div>
        <div class="glass p-4 rounded-2xl text-center border-b-4 border-blue-500">
            <i class="fab fa-react text-blue-500 text-2xl mb-2"></i>
            <h4 class="font-bold text-xs uppercase tracking-widest">React / Next.js</h4>
            <p class="text-[10px] text-gray-400">Next Gen Tech</p>
        </div>
    </div>

    <!-- Input Area -->
    <textarea id="userInput" class="w-full max-w-4xl h-40 glass rounded-2xl p-4 mb-4 outline-none focus:border-blue-500" placeholder="Paste URL or Describe layout..."></textarea>
    
    <button onclick="process()" class="bg-blue-600 px-8 py-3 rounded-full font-bold hover:scale-105 transition">Generate Magic ✨</button>

    <!-- Result Display & Download -->
    <div id="resultBox" class="hidden w-full max-w-4xl mt-10 p-6 glass rounded-2xl">
        <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold">Output Result:</h3>
            <button id="downloadBtn" class="bg-green-600 text-xs px-4 py-2 rounded-lg font-bold">⬇️ Download File</button>
        </div>
        <pre id="outputText" class="whitespace-pre-wrap text-sm text-gray-300"></pre>
    </div>

    <script>
        let currentMode = 'clone';
        function setMode(m) { currentMode = m; alert("Mode set to: " + m); }

        async function process() {
            const text = document.getElementById('userInput').value;
            const resBox = document.getElementById('resultBox');
            const outText = document.getElementById('outputText');
            
            resBox.classList.remove('hidden');
            outText.innerText = "Processing... Please wait.";

            const formData = new FormData();
            formData.append('mode', currentMode);
            formData.append('text', text);

            const response = await fetch('/process', { method: 'POST', body: formData });
            const data = await response.json();

            if(data.status === 'success') {
                outText.innerText = data.result;
                document.getElementById('downloadBtn').onclick = () => {
                    const blob = new Blob([data.result], { type: 'text/plain' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = data.file_name;
                    a.click();
                };
            }
        }
    </script>
</body>
</html>
