from flask import Flask
from threading import Thread
import requests, time

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=5000)

def ping_self():
    while True:
        try:
            requests.get("https://bcoy-bot.onrender.com")  # 👈 change this
        except:
            pass
        time.sleep(240)  # every 4 minutes

def keep_alive():
    Thread(target=run).start()
    Thread(target=ping_self).start()
