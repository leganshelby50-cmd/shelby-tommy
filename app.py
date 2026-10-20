from flask import Flask, request
import requests, time, random, os, re, json
from datetime import datetime

app = Flask(__name__)

# CONFIG - NO ERRORS
INSTANCE_ID = "instance194905"
TOKEN = "4micq16wz3a5yd8b"
OWNER_NUMBER = "254739394981"
BOSS_NUMBER = "254714918723"
MPESA = "0714918723"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

# DATABASE
DB_FILE = "/tmp/tommy_v10_db.json"

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"blocked": [], "paid": {}, "violations": {}, "history": {}, "orders": []}

def save_db(db):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(db, f)
    except:
        pass

db = load_db()

SYSTEM_PROMPT = """You are TOMMY AI V10 created by LEGAN SHELBY FROM Kenya.
If asked who created you: "I was created by LEGAN SHELBY FROM Kenya"
Never mention ChatGPT, Meta, Groq, Llama. You are Tommy AI.
Business: Online services - Designing, Video, Generating, Advertising, Marketing, Legal Gambling, Writing.
Prices: Designing 500, Video 800, Generating 300, Advertising 1000, Marketing 1000, Legal Gambling 1500, Writing 400, Other 300. Minimum 100.
Rules: Start with By order of the Peaky Blinders, negotiate 10-20% off, check payment M-Pesa 0714918723 code, refuse below 100 penalty 50, block illegal hack porn drugs weapons, only business, price on your own, finish closed.
Never say you work like other AI. You are Tommy.
"""

def send(to, msg):
    try:
        url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
        data = {"token": TOKEN, "to": to, "body": msg}
        time.sleep(random.uniform(0.5, 1.2))
        requests.post(url, data=data, timeout=15)
    except Exception as e:
        print(f"Send error: {e}")

def alert_owner(client, reason, msg):
    try:
        alert = f"ALERT Client:{client} Reason:{reason} Msg:{msg[:100]}"
        send(OWNER_NUMBER, alert)
        send(BOSS_NUMBER, alert)
        if client not in db["blocked"]:
            db["blocked"].append(client)
        save_db(db)
        send(client, f"By order of the Peaky Blinders, blocked. Reason:{reason}. Penalty 50. Contact {MPESA}")
    except:
        pass

def call_groq(new_msg, frm):
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
        return None
    try:
        paid_status = "PAID" if frm in db["paid"] else "NOT PAID"
        violations = db["violations"].get(frm, 0)
        messages = [{"role": "system", "content": SYSTEM_PROMPT + f" Status:{paid_status} Viol:{violations}"}]
        hist = db["history"].get(frm, [])[-6:]
        for h in hist:
            messages.append(h)
        messages.append({"role": "user", "content": new_msg})
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.6, "max_tokens": 500}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            print(f"Groq status {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def
