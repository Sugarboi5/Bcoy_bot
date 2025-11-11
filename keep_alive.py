from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run():
    """Run Flask server on port 5000"""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def keep_alive():
    """Start Flask server in background thread"""
    server_thread = Thread(target=run, daemon=True)
    server_thread.start()
    print("✅ Keep-alive server started on port 5000")