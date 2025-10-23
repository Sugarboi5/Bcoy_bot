# keep_alive.py
# This file creates a tiny Flask web server to keep your bot online
# Works great with Replit + UptimeRobot or similar setups

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is alive and running!"

def run():
    # Run the web server on port 8080 (default for Replit)
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Start the web server in a separate thread
    t = Thread(target=run)
    t.start()
