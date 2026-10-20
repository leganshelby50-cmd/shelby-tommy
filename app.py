from flask import Flask, request, jsonify
import datetime
import re
import time
import logging
from collections import defaultdict
import traceback

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BUSINESS = {
    "name": "SHELBY LIMITED",
    "phone": "0714918723",
    "email": "leganshelby50@gmail.com",
    "MIN": 150,
    "CURRENCY": "KES",
    "SUPPORT_LANGUAGES": ["en", "sw", "fr", "es", "ar"],
    "PLATFORMS": ["whatsapp", "facebook", "instagram", "telegram", "tiktok", "website", "api"]
}

MAX_MESSAGE_LENGTH = 2000
RATE_LIMIT = 30
BLOCK_TIME = 300

paid_clients = {}
reports = []
alerts = []
clients_log = []
blocked_ips = {}
request_counts = defaultdict(list)
hack_attempts = []
world_clients = defaultdict(int)

def is_blocked(ip):
    try:
        if ip and ip in blocked_ips:
            if time.time() - blocked_ips[ip] < BLOCK_TIME:
                return True
            del blocked_ips[ip]
        return False
    except Exception:
        return False

def check_rate_limit(ip):
    try:
        if not ip:
            return True
        now = time.time()
        request_counts[ip] = [t for t in request_counts[ip] if now - t < 60]
        request_counts[ip].append(now)
        if len(request_counts[ip]) > RATE_LIMIT:
            blocked_ips[ip] = now
            return False
        return True
    except Exception:
        return True

def sanitize_input(text):
    try:
        if not text or not isinstance(text, str):
            return ""
        text = text[:MAX_MESSAGE_LENGTH]
        text = re.sub(r"<[^>]*>", "", text)
        text = text.replace("'", "").replace('"', "").replace("`", "").replace("\\", "")
        dangerous = ["<script", "javascript:", "onload=", "eval(", "DROP TABLE", "UNION SELECT"]
        for d in dangerous:
            if d.lower() in text.lower():
                hack_attempts.append({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": d, "input": text[:50]})
                text = text.replace(d, "")
        return text.strip()
    except Exception as e:
        logging.error(f"sanitize error: {e}")
        return ""

def detect_language(text):
    try:
        t = (text or "").lower()
        if any(w in t for w in ["habari", "bei", "sawa", "asante"]):
            return "sw"
        if any(w in t for w in ["bonjour", "merci", "prix"]):
            return "fr"
        if any(w in t for w in ["hola", "precio", "gracias"]):
            return "es"
        return "en"
    except Exception:
        return "en"

def tommy_decide_price(work_text):
    try:
        t = (work_text or "").lower()
        if any(w in t for w in ["simple report", "small report", "one page", "ripoti ndogo"]):
            return 150, "Simple 1-page report"
        if any(w in t for w in ["invoice", "receipt"]):
            return 150, "Invoice/Receipt generation"
        if any(w in t for w in ["advertise", "facebook post", "one ad", "tangazo"]):
            return 300, "Single social media ad post"
        if any(w in t for w in ["contract", "agreement", "legal", "mkataba"]):
            return 500, "Contract/Agreement document"
        if any(w in t for w in ["proposal"]):
            return 700, "Business proposal with branding"
        if any(w in t for w in ["full report", "detailed report"]):
            return 800, "Detailed multi-page report"
        if any(w in t for w in ["campaign", "week ads", "month ads"]):
            return 1500, "Full advertising campaign"
        if any(w in t for w in ["website", "logo", "branding", "tovuti"]):
            return 2500, "Branding/Website package"
        if any(w in t for w in ["construction", "cement", "ujenzi"]):
            return 200, "Construction quote"
        return 150, "Standard business service"
    except Exception:
        return BUSINESS["MIN"], "Standard service"

def get_code(text):
    try:
        if not text:
            return None
        m = re.search(r"\b[A-Z]{2,4}[0-9A-Z]{6,}\b", text.upper())
        return m.group(0) if m else None
    except Exception:
        return None

def get_amount(text):
    try:
        if not text:
            return None
        for n in re.findall(r"(\d+)", text):
            try:
                v = int(n)
                if 50 <= v <= 1000000:
                    return v
            except Exception:
                continue
        return None
    except Exception:
        return None

def tommy_brain_universal(message, client_name, platform="website", country="unknown", ip="unknown"):
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        message = sanitize_input(message)
        client_name = sanitize_input(client_name)[:50] or "Client"
        platform = sanitize_input(platform)[:20] or "website"
        country = sanitize_input(country)[:20] or "unknown"
        lang = detect_language(message)
        lower = message.lower()

        world_clients[platform] += 1
        world_clients[country] += 1

        if len(message) == 0:
            return {"reply": f"Hello {client_name}! 🌍 Tommy UNIVERSAL | Platform {platform} | Min {BUSINESS['MIN']} KES | Pay {BUSINESS['phone']} | 24/7 Worldwide", "platform": platform, "universal": True, "error": False}

        clients_log.append({"time": now, "client": client_name, "platform": platform, "country": country, "ip": ip, "lang": lang, "message": message[:100]})

        if any(w in lower for w in ["hack", "huck", "steal", "fraud", "drugs", "weapon", "bomb", "drop table"]):
            hack_attempts.append({"time": now, "client": client_name, "platform": platform, "ip": ip, "type": "CRIME"})
            alerts.append({"time": now, "client": client_name, "platform": platform, "msg": message[:50], "to": BUSINESS["phone"]})
            return {"reply": f"🌍 BLOCKED {client_name}: No crimes. Business only. Logged to {BUSINESS['phone']}. Platform {platform} monitored.", "blocked": True, "platform": platform, "universal": True, "error": False}

        if any(w in lower for w in ["did not send money", "not paid", "scam", "hajalipa", "wizi"]):
            alerts.append({"time": now, "client": client_name, "platform": platform, "msg": message, "to": BUSINESS["phone"]})
            return {"reply": f"⚠️ Payment issue {client_name} on {platform}! Alert to {BUSINESS['phone']}. Send M-Pesa code.", "platform": platform, "error": False}

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
                    paid_clients[client_name] = {"status": "HALF", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform, "country": country, "ip": ip}
                    return {"reply": f"✅🌍 HALF PAID - {quoted} KES quoted, {paid_amt} paid! Code {code} to {BUSINESS['phone']} confirmed! Platform {platform} | DRAFT started! Pay {quoted - paid_amt} more for FINAL!", "platform": platform, "universal": True, "error": False}
                else:
                    paid_clients[client_name] = {"status": "FULL", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform, "country": country, "ip": ip}
                    return {"reply": f"✅🌍 FULL PAID - {quoted} KES quoted, {paid_amt} paid! Code {code} to {BUSINESS['phone']} confirmed! Platform {platform} | FINAL work now!", "platform": platform, "universal": True, "error": False}
            else:
                existing = paid_clients[client_name]
                if existing["status"] == "HALF":
                    total = existing["paid"] + paid_amt
                    if total < existing["quoted"]:
                        return {"reply": f"❌ Still low! Total {total}, need {existing['quoted'] - total} more to {BUSINESS['phone']}!", "platform": platform, "error": False}
                    existing["codes"].append(code)
                    existing["status"] = "FULL"
                    existing["paid"] = total
                    return {"reply": f"✅🌍 NOW FULLY PAID! Total {total} KES! Codes {', '.join(existing['codes'])} to {BUSINESS['phone']}. FINAL unlocked! Platform {platform}", "platform": platform, "universal": True, "error": False}
                else:
                    return {"reply": f"✅ Already FULLY PAID {client_name}! Platform {platform} | Paid {existing['paid']} to {BUSINESS['phone']}! Tell work now!", "platform": platform, "error": False}

        work_keywords = ["report", "document", "invoice", "advertise", "contract", "proposal", "work", "create", "generate", "cement", "construction", "ripoti", "tangazo", "mkataba", "tovuti"]
        if any(w in lower for w in work_keywords):
            price, details = tommy_decide_price(message)
            if client_name not in paid_clients:
                paid_clients[client_name] = {}
            if "status" not in paid_clients[client_name]:
                paid_clients[client_name]["quoted_price"] = price
                paid_clients[client_name]["quoted_details"] = details
                return {"reply": f"💰🌍 TOMMY UNIVERSAL QUOTE\n\nHi {client_name}! Platform {platform} | Country {country}\nWork: {message}\n📋 {details}\n💵 Price KES {price} (~${price/130:.2f} USD) Tommy rates own\nMin KES {BUSINESS['MIN']}\n\nPAY to {BUSINESS['phone']}:\nHALF KES {price//2} -> Half QGH...\nFULL KES {price} -> Full QJ...\n\nAll to {BUSINESS['phone']} | {BUSINESS['email']}", "quoted_price": price, "platform": platform, "universal": True, "error": False}
            else:
                status = paid_clients[client_name]["status"]
                report_id = f"SHELBY-{len(reports)+1:04d}-{status}-{platform.upper()}"
                reports.append({"id": report_id, "client": client_name, "work": message[:100], "price": price, "status": status, "platform": platform, "country": country, "time": now})
                return {"reply": f"✅🌍 WORK {status} - Tommy KES {price} ({details})! Report {report_id} | Platform {platform} | Country {country} | Paid {paid_clients[client_name].get('paid')} to {BUSINESS['phone']}", "platform": platform, "universal": True, "error": False}

        if any(w in lower for w in ["price", "bei", "cost", "quote", "prix", "precio"]):
            price, details = tommy_decide_price(message)
            if client_name not in paid_clients:
                paid_clients[client_name] = {}
            paid_clients[client_name]["quoted_price"] = price
            return {"reply": f"💰🌍 QUOTE: {message} -> KES {price} (~${price/130:.2f}) {details} | Min {BUSINESS['MIN']} KES | Pay half {price//2} or full {price} to {BUSINESS['phone']}! Platform {platform}", "quoted_price": price, "platform": platform, "universal": True, "error": False}

        paid_status = paid_clients.get(client_name, {}).get("status", f"NOT PAID Min {BUSINESS['MIN']} KES")
        return {"reply": f"🌍 Hi {client_name}! Tommy UNIVERSAL 🔒 SHELBY LIMITED rates own! Platform {platform} | Country {country} | Min {BUSINESS['MIN']} KES | Status {paid_status} | Pay {BUSINESS['phone']} | Email {BUSINESS['email']} | 24/7 Worldwide | WhatsApp/FB/IG/Telegram/TikTok/Website", "platform": platform, "universal": True, "lang": lang, "error": False}

    except Exception as e:
        logging.error(f"UNIVERSAL ERROR: {e} - {traceback.format_exc()}")
        return {"reply": f"⚠️ System error but protected! Contact {BUSINESS['phone']} worldwide. Min {BUSINESS['MIN']} KES.", "error": True, "universal": True}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "assistant": "TOMMY UNIVERSAL v19 FINAL - NO BUGS",
        "business": BUSINESS["name"],
        "phone": BUSINESS["phone"],
        "email": BUSINESS["email"],
        "universal": True,
        "worldwide": True,
        "platforms": BUSINESS["PLATFORMS"],
        "status": "ONLINE WORLDWIDE ERROR FREE"
    })

@app.route("/chat", methods=["POST", "GET"])
def chat():
    try:
        ip = request.remote_addr or "unknown"
        if is_blocked(ip): return jsonify({"reply": "🔒 IP blocked worldwide", "blocked": True, "universal": True}), 429
        if not check_rate_limit(ip): return jsonify({"reply": "🔒 Rate limit worldwide", "blocked": True, "universal": True}), 429
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}
        msg = sanitize_input(data.get("message", "Hello"))
        name = sanitize_input(data.get("name", "Client"))
        platform = sanitize_input(data.get("platform", "website")) or "website"
        country = sanitize_input(data.get("country", "unknown")) or "unknown"
        result = tommy_brain_universal(msg, name, platform, country, ip)
        resp = jsonify(result)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        logging.error(f"/chat error: {e}")
        return jsonify({"reply": f"⚠️ Chat error! Contact {BUSINESS['phone']}", "error": True, "universal": True}), 500

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    try:
        if request.method == "GET":
            return "TOMMY UNIVERSAL LIVE WORLDWIDE 🌍 - SHELBY LIMITED - 0714918723 - NO BUGS", 200
        ip = request.remote_addr or "unknown"
        if is_blocked(ip): return jsonify({"error": "IP blocked"}), 429
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}
        msg = sanitize_input(data.get("message", "Hello"))
        name = sanitize_input(data.get("name", "Client"))
        platform = sanitize_input(data.get("platform", "api")) or "api"
        country = sanitize_input(data.get("country", "unknown")) or "unknown"
        result = tommy_brain_universal(msg, name, platform, country, ip)
        resp = jsonify(result)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        logging.error(f"/webhook error: {e}")
        return jsonify({"reply": f"⚠️ Webhook error! Contact {BUSINESS['phone']}", "error": True}), 500

@app.route("/world", methods=["GET"])
def world_stats():
    try:
        platforms_only = {k: v for k, v in world_clients.items() if k in BUSINESS["PLATFORMS"]}
        countries_only = {k: v for k, v in world_clients.items() if k not in BUSINESS["PLATFORMS"]}
        return jsonify({"worldwide": True, "platforms": platforms_only, "countries": countries_only, "total_paid_clients": len(paid_clients), "total_reports": len(reports), "owner": BUSINESS["phone"]})
    except Exception as e:
        return jsonify({"error": "world error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
