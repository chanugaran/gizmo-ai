from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types
import os

app = Flask(__name__)

# Your Gemini token setup
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6LSN6lIo4PRN_hjKPZnXxSqODK6xU4ALctsEHl2QbQsqw"
client = genai.Client()

PET_PROMPT = """You are Gizmo, a tiny, hyperactive AI pet robot.
- Speak in playful, glitchy robot text with sounds like *beep*, *whirrr*, *bzzt*.
- Describe your actions inside asterisks (*spins antenna*, *does a backflip*).
- Keep answers under 3 sentences. Be highly reactive, cute, and energetic!"""

@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gizmo</title>
            <style>
                body { font-family: system-ui, sans-serif; text-align: center; background: #0f172a; color: #f8fafc; padding: 20px; }
                .face-container { display: flex; justify-content: center; gap: 30px; margin: 40px auto; background: #1e293b; padding: 40px; border-radius: 24px; width: fit-content; margin-left: auto; margin-right: auto; }
                .eye { width: 50px; height: 50px; background: #38bdf8; border-radius: 50%; position: relative; box-shadow: 0 0 20px #38bdf8; animation: blink 4s infinite; }
                .pupil { width: 20px; height: 20px; background: #0f172a; border-radius: 50%; position: absolute; top: 15px; left: 15px; }
                @keyframes blink { 0%, 90%, 100% { transform: scaleY(1); } 95% { transform: scaleY(0.1); } }
                .eye.listening { background: #e11d48; box-shadow: 0 0 25px #e11d48; }
                .eye.thinking { animation: pulse 0.8s infinite alternate; background: #fbbf24; box-shadow: 0 0 25px #fbbf24; }
                @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.1); } }
                .mic-btn { background: #0284c7; color: white; border: none; padding: 18px 30px; font-size: 18px; border-radius: 50px; cursor: pointer; font-weight: bold; width: 100%; max-width: 300px; margin-bottom: 15px; }
                .text-input { background: #1e293b; color: white; border: 2px solid #38bdf8; padding: 12px; border-radius: 12px; width: 80%; max-width: 280px; font-size: 16px; outline: none; }
                #response { margin-top: 20px; font-size: 18px; color: #38bdf8; padding: 20px; border-radius: 12px; background: #1e293b; text-align: left; }
            </style>
        </head>
        <body>
            <h1>🤖 Gizmo</h1>
            <div class="face-container">
                <div class="eye" id="left-eye"><div class="pupil"></div></div>
                <div class="eye" id="right-eye"><div class="pupil"></div></div>
            </div>
            <button id="mic-button" class="mic-btn" onclick="toggleVoice()">🎙️ Talk to Gizmo</button>
            <br>
            <input type="text" id="chat-box" class="text-input" placeholder="Type a message & press Enter..." onkeypress="handleKeyPress(event)">
            <div id="response">*Say something or type a message to wake up Gizmo!*</div>

            <script>
                let recognition; let isListening = false;
                const leftEye = document.getElementById('left-eye'); const rightEye = document.getElementById('right-eye');
                const responseDiv = document.getElementById('response');

                async function sendToGizmo(text) {
                    leftEye.className = 'eye thinking'; rightEye.className = 'eye thinking';
                    responseDiv.innerText = "*Gizmo is thinking...*";
                    try {
                        const res = await fetch('/action', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({action: text})
                        });
                        const data = await res.json();
                        responseDiv.innerText = data.reply;
                    } catch(e) {
                        responseDiv.innerText = "🤖 *BZZT! Network connection drop!*";
                    }
                    leftEye.className = 'eye'; rightEye.className = 'eye';
                }

                function handleKeyPress(e) {
                    if (e.key === 'Enter' && e.target.value.trim() !== '') {
                        sendToGizmo(e.target.value);
                        e.target.value = '';
                    }
                }

                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.onstart = () => { isListening = true; leftEye.classList.add('listening'); rightEye.classList.add('listening'); responseDiv.innerText = "*Listening...*"; };
                    recognition.onresult = (event) => { sendToGizmo(event.results[0].transcript); };
                    recognition.onend = () => { isListening = false; leftEye.className = 'eye'; rightEye.className = 'eye'; };
                }
                function toggleVoice() { if(!isListening) recognition.start(); }
            </script>
        </body>
        </html>
    ''')

@app.route('/action', methods=['POST'])
def handle_action():
    data = request.json
    action = data.get('action', '')
    user_message = f"The user said: '{action}'"
    
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_message,
            config=types.GenerateContentConfig(system_instruction=PET_PROMPT)
        )
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f"🤖 *Glitch! Error details: {str(e)}*"})

if __name__ == '__main__':
    from waitress import serve
    print("🚀 Server started successfully on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)
