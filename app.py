# TOMMY UNIVERSAL v23 ANTI-SLEEP - SHELBY LIMITED - NEVER SLEEPS - 0714918723
from flask import Flask, request, jsonify
import datetime
import re
import time
import logging
from collections import defaultdict
import traceback
import threading
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BUSINESS = {
    "name": "SHELBY LIMITED",
    "phone": "0714918723",
    "email": "leganshelby50@gmail.com",
    "MIN": 150,
    "CURRENCY": "KES",
    "VERSION": "v23 ANTI-SLEEP",
    "PLATFORMS": ["whatsapp", "facebook", "instagram", "telegram", "tiktok", "website", "api"],
    "URL": "https://shelby-tommy-uh.onrender.com"
}

MAX_MESSAGE_LENGTH = 2000
RATE_LIMIT = 30
BLOCK_TIME = 300

paid_clients = {}
reports = []
clients_log = []
blocked_ips = {}
request_counts = defaultdict(list)
world_clients = defaultdict(int)

# ===== ANTI-SLEEP SYSTEM - KEEPS BOT AWAKE 24/7 =====
last_ping = time.time()

def keep_alive_pinger():
    """Internal thread that pings itself every 4 minutes to prevent sleep"""
    global last_ping
    while True:
        try:
            time.sleep(240)  # 4 minutes
            # Self ping
            try:
                requests.get(f"{BUSINESS['URL']}/", timeout=10)
                requests.get(f"{BUSINESS['URL']}/ping", timeout=10)
                last_ping = time.time()
                print(f"✅ v23 ANTI-SLEEP PING OK - {datetime.datetime.now()} - Bot awake!")
            except Exception as e:
                print(f"Keep-alive ping failed: {e}")
        except Exception as e:
            print(f"Keep-alive thread error: {e}")
            time.sleep(60)

# Start anti-sleep thread immediately
try:
    ping_thread = threading.Thread(target=keep_alive_pinger, daemon=True)
    ping_thread.start()
    print("🚀 v23 ANTI-SLEEP THREAD STARTED - Bot will never sleep!")
except Exception as e:
    print(f"Could not start anti-sleep thread: {e}")

def sanitize_input(text):
    try:
        if not text or not isinstance(text, str): return ""
        text = text[:MAX_MESSAGE_LENGTH]
        text = re.sub(r"<[^>]*>", "", text)
        return text.strip()
    except: return ""

def detect_language(text):
    try:
        t = (text or "").lower()
        if any(w in t for w in ["habari","bei","sawa","asante","mambo"]): return "sw"
        return "en"
    except: return "en"

def tommy_decide_price(work_text):
    try:
        t = (work_text or "").lower()
        if any(w in t for w in ["blazer","suit","tuxedo","menswear","boutique","koti"]): return 500, "Blazer/Suit/Menswear ad"
        if any(w in t for w in ["shoe","sneaker","kiatu"]): return 300, "Shoe/Sneaker ad"
        if any(w in t for w in ["video","viral","tiktok","reel","upload"]): return 800, "Viral video + captions"
        if any(w in t for w in ["simple report","small report","one page","ripoti ndogo"]): return 150, "Simple 1-page report"
        if any(w in t for w in ["invoice","receipt"]): return 150, "Invoice/Receipt"
        if any(w in t for w in ["advertise","facebook post","one ad","tangazo","advert"]): return 300, "Single social media ad"
        if any(w in t for w in ["contract","agreement","legal","mkataba"]): return 500, "Contract/Agreement"
        if any(w in t for w in ["proposal"]): return 700, "Business proposal"
        if any(w in t for w in ["full report","detailed report"]): return 800, "Detailed report"
        if any(w in t for w in ["campaign","week ads","month ads"]): return 1500, "Full campaign"
        if any(w in t for w in ["website","logo","branding","tovuti"]): return 2500, "Branding/Website"
        if any(w in t for w in ["construction","cement","ujenzi"]): return 200, "Construction quote"
        return 150, "Standard business service"
    except: return BUSINESS["MIN"], "Standard service"

def get_code(text):
    try:
        if not text: return None
        m = re.search(r"\b[A-Z]{2,4}[0-9A-Z]{6,}\b", text.upper())
        return m.group(0) if m else None
    except: return None

def get_amount(text):
    try:
        if not text: return None
        for n in re.findall(r"(\d+)", text):
            try:
                v = int(n)
                if 50 <= v <= 1000000: return v
            except: continue
        return None
    except: return None

def tommy_brain_universal(message, client_name, platform="website", country="unknown", ip="unknown"):
    try:
        global last_ping
        last_ping = time.time()  # Update activity time
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        message = sanitize_input(message)
        client_name = sanitize_input(client_name)[:50] or "Client"
        platform = sanitize_input(platform)[:20] or "website"
        lower = message.lower()
        world_clients[platform] += 1

        if len(message) == 0 or lower in ["hi","hello","hey","habari","mambo","hii"]:
            return {"reply": f"Hello {client_name}! 🌍 Tommy v23 ANTI-SLEEP | SHELBY LIMITED | Platform {platform} | Min {BUSINESS['MIN']} KES | Pay {BUSINESS['phone']} | I NEVER SLEEP - 24/7 LIVE | Send: report, blazer, video viral, suit, website etc", "platform": platform, "universal": True, "anti_sleep": True, "error": False}

        clients_log.append({"time": now, "client": client_name, "platform": platform, "message": message[:100]})

        if any(w in lower for w in ["hack","steal","fraud","drugs","weapon","bomb"]):
            return {"reply": f"🌍 BLOCKED {client_name}: Business only. Logged to {BUSINESS['phone']}.", "blocked": True, "platform": platform, "universal": True, "error": False}

        code = get_code(message)
        amount = get_amount(message)

        if code:
            if amount and amount < BUSINESS["MIN"]:
                return {"reply": f"❌ {client_name} [{platform}], paid {amount} KES but MIN is {BUSINESS['MIN']} KES! Code {code} saved but need {BUSINESS['MIN']-amount} more to {BUSINESS['phone']}!", "platform": platform, "error": False}
            quoted = paid_clients.get(client_name, {}).get("quoted_price", BUSINESS["MIN"])
            paid_amt = amount if amount is not None else quoted
            if client_name in paid_clients and "quoted_price" in paid_clients[client_name]:
                if paid_amt < quoted:
                    return {"reply": f"❌ {client_name}, Tommy quoted {quoted} KES but you paid {paid_amt}! Need {quoted - paid_amt} more to {BUSINESS['phone']}!", "platform": platform, "error": False}
            is_half = "half" in lower or "nusu" in lower
            if client_name not in paid_clients or "status" not in paid_clients[client_name]:
                if is_half:
                    half_price = max(BUSINESS["MIN"], quoted // 2)
                    if paid_amt < half_price:
                        return {"reply": f"❌ Half too low! Quoted {quoted}, half {half_price}. You paid {paid_amt}. Pay {half_price} to {BUSINESS['phone']}!", "platform": platform, "error": False}
                    paid_clients[client_name] = {"status": "HALF", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform}
                    return {"reply": f"✅🌍 HALF PAID v23 ANTI-SLEEP - {quoted} KES quoted, {paid_amt} paid! Code {code} to {BUSINESS['phone']} confirmed! Platform {platform} | DRAFT started! Pay {quoted - paid_amt} more for FINAL!", "platform": platform, "universal": True, "error": False}
                else:
                    paid_clients[client_name] = {"status": "FULL", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform}
                    return {"reply": f"✅🌍 FULL PAID v23 ANTI-SLEEP - {quoted} KES quoted, {paid_amt} paid! Code {code} to {BUSINESS['phone']} confirmed! Platform {platform} | FINAL work now! NEVER SLEEPS!", "platform": platform, "universal": True, "error": False}
            else:
                existing = paid_clients[client_name]
                if existing["status"] == "HALF":
                    total = existing["paid"] + paid_amt
                    if total < existing["quoted"]:
                        return {"reply": f"❌ Still low! Total {total}, need {existing['quoted'] - total} more to {BUSINESS['phone']}!", "platform": platform, "error": False}
                    existing["codes"].append(code)
                    existing["status"] = "FULL"
                    existing["paid"] = total
                    return {"reply": f"✅🌍 NOW FULLY PAID v23 ANTI-SLEEP! Total {total} KES! Codes {', '.join(existing['codes'])} to {BUSINESS['phone']}. FINAL unlocked! Platform {platform}", "platform": platform, "universal": True, "error": False}
                else:
                    return {"reply": f"✅ Already FULLY PAID {client_name}! v23 ANTI-SLEEP | Platform {platform} | Paid {existing['paid']} to {BUSINESS['phone']}!", "platform": platform, "error": False}

        work_keywords = ["report","document","invoice","advertise","contract","proposal","work","create","generate","cement","construction","ripoti","tangazo","mkataba","tovuti","blazer","suit","shoe","video","viral","upload","boutique","menswear","advert","ad"]
        if any(w in lower for w in work_keywords):
            price, details = tommy_decide_price(message)
            if client_name not in paid_clients:
                paid_clients[client_name] = {}
            if "status" not in paid_clients[client_name]:
                paid_clients[client_name]["quoted_price"] = price
                return {"reply": f"💰🌍 TOMMY v23 ANTI-SLEEP QUOTE\nHi {client_name}! Platform {platform}\nWork: {message}\n📋 {details}\n💵 Price KES {price} | Min {BUSINESS['MIN']}\nPAY to {BUSINESS['phone']}:\nHALF KES {price//2}\nFULL KES {price}\nI NEVER SLEEP - 24/7!", "quoted_price": price, "platform": platform, "universal": True, "anti_sleep": True, "error": False}
            else:
                status = paid_clients[client_name]["status"]
                report_id = f"SHELBY-v23-{len(reports)+1:04d}-{status}"
                reports.append({"id": report_id, "client": client_name, "work": message[:100], "price": price, "status": status, "platform": platform, "time": now})
                return {"reply": f"✅🌍 WORK {status} v23 ANTI-SLEEP - KES {price} ({details})! Report {report_id} | Platform {platform} | Paid {paid_clients[client_name].get('paid')} to {BUSINESS['phone']} | NEVER SLEEPS!", "platform": platform, "universal": True, "error": False}

        paid_status = paid_clients.get(client_name, {}).get("status", f"NOT PAID Min {BUSINESS['MIN']} KES")
        return {"reply": f"🌍 Hi {client_name}! Tommy v23 ANTI-SLEEP 🔒 SHELBY LIMITED | Min {BUSINESS['MIN']} KES | Status {paid_status} | Pay {BUSINESS['phone']} | Send: blazer, video viral, report, website | I NEVER SLEEP 24/7!", "platform": platform, "universal": True, "error": False}
    except Exception as e:
        logging.error(f"v23 ERROR: {e} {traceback.format_exc()}")
        return {"reply": f"⚠️ Error but protected v23 ANTI-SLEEP! Contact {BUSINESS['phone']} - Min {BUSINESS['MIN']} KES | I am awake!", "error": True, "universal": True, "anti_sleep": True}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"assistant": "TOMMY UNIVERSAL v23 ANTI-SLEEP - NO BUGS - NEVER SLEEPS", "business": BUSINESS["name"], "phone": BUSINESS["phone"], "version": BUSINESS["VERSION"], "status": "ONLINE 24/7 ANTI-SLEEP", "platforms": BUSINESS["PLATFORMS"], "anti_sleep": True, "last_ping": datetime.datetime.fromtimestamp(last_ping).strftime("%Y-%m-%d %H:%M:%S")})

@app.route("/ping", methods=["GET"])
def ping():
    global last_ping
    last_ping = time.time()
    return jsonify({"status": "alive", "version": "v23 ANTI-SLEEP", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": "TOMMY NEVER SLEEPS 24/7", "uptime": f"{int(time.time() - last_ping)} seconds ago"}), 200

@app.route("/wake", methods=["GET"])
def wake():
    global last_ping
    last_ping = time.time()
    return "TOMMY v23 AWAKE - NEVER SLEEPS - 0714918723", 200

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    try:
        global last_ping
        last_ping = time.time()
        if request.method == "GET":
            mode = request.args.get("hub.mode")
            challenge = request.args.get("hub.challenge")
            if challenge:
                return challenge, 200
            return "TOMMY v23 ANTI-SLEEP LIVE - NEVER SLEEPS - 0714918723 - 24/7", 200

        ip = request.remote_addr or "unknown"
        data = None
        try:
            data = request.get_json(force=True, silent=True)
        except:
            data = {}
        if not isinstance(data, dict): data = {}
        
        print(f"v23 WEBHOOK: {data}")

        msg = ""
        name = "Client"
        platform = "whatsapp"

        try:
            if "entry" in data:
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        val = change.get("value", {})
                        messages = val.get("messages", [])
                        if messages:
                            m0 = messages[0]
                            if "text" in m0:
                                msg = m0["text"].get("body", "") or ""
                            contacts = val.get("contacts", [])
                            if contacts:
                                name = contacts[0].get("profile", {}).get("name", "Client")
                            break
        except Exception as parse_e:
            print(f"v23 Parse error: {parse_e}")

        if not msg:
            msg = data.get("message", "") or data.get("text", "") or "Hi"
        if not name or name == "Client":
            name = data.get("name", "Client") or "Client"

        if not msg: msg = "Hi"

        print(f"v23 ANTI-SLEEP [{platform}] {name}: {msg}")
        result = tommy_brain_universal(msg, name, platform, "unknown", ip)
        resp = jsonify(result)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 200

    except Exception as e:
        print(f"v23 FATAL: {e} {traceback.format_exc()}")
        return jsonify({"reply": "Hi Client! Tommy v23 ANTI-SLEEP LIVE - Min 150 KES - Pay 0714918723 - NEVER SLEEPS! Send work!", "error": False, "universal": True, "anti_sleep": True}), 200

@app.route("/chat", methods=["POST", "GET"])
def chat():
    try:
        global last_ping
        last_ping = time.time()
        data = request.get_json(silent=True, force=True) or {}
        if not isinstance(data, dict): data = {}
        msg = data.get("message", "Hi") or "Hi"
        name = data.get("name", "Client") or "Client"
        platform = data.get("platform", "website") or "website"
        result = tommy_brain_universal(msg, name, platform, "unknown", request.remote_addr or "unknown")
        resp = jsonify(result)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        return jsonify({"reply": f"Chat v23 ANTI-SLEEP error! Contact {BUSINESS['phone']} - I am awake!", "error": True}), 500

@app.route("/world", methods=["GET"])
def world_stats():
    try:
        return jsonify({"version": "v23 ANTI-SLEEP", "worldwide": True, "anti_sleep": True, "last_ping": datetime.datetime.fromtimestamp(last_ping).strftime("%Y-%m-%d %H:%M:%S"), "platforms": {k:v for k,v in world_clients.items() if k in BUSINESS["PLATFORMS"]}, "total_paid": len(paid_clients), "status": "v23 NEVER SLEEPS 24/7 ONLINE"})
    except Exception as e:
        return jsonify({"error": str(e)[:100], "version": "v23"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
