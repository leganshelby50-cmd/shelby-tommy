# =============================================================================
# TOMMY v33 FINAL - ORIGINAL INSTRUCTIONS - SHELBY LIMITED COMPANY
# TOMMY AI - NOT BOT - SHARP IQ - TOMMY SHELBY VOICE - NO ERRORS
# OWNER ALERT: 0739394981 | BUSINESS: 0714918723 | MIN 100 KES
# =============================================================================
from flask import Flask, request, jsonify
import datetime, re, time, logging, traceback, threading
from collections import defaultdict

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BUSINESS = {
    "name": "SHELBY LIMITED COMPANY",
    "phone": "0714918723",
    "alert_phone": "0739394981",
    "email": "leganshelby50@gmail.com",
    "MIN": 100,
    "PENALTY": 50,
    "VERSION": "v33 ORIGINAL FINAL",
    "URL": "https://shelby-tommy-uh.onrender.com",
    "ULTRAMSG_INSTANCE": "instance194905",
    "ULTRAMSG_TOKEN": "4micq16wz3a5yd8b",
}

paid_clients = {}
reports = []
clients_log = []
world_clients = defaultdict(int)
blocked_clients = {}
violations = defaultdict(int)
last_ping = time.time()

# ANTI-SLEEP
def keep_alive():
    global last_ping
    while True:
        try:
            time.sleep(240)
            last_ping = time.time()
            if HAS_REQUESTS:
                try: requests.get(f"{BUSINESS['URL']}/ping", timeout=8)
                except: pass
        except: time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()

def clean(t):
    if not t or not isinstance(t, str): return ""
    return re.sub(r"<[^>]*>", "", t)[:2000].strip()

def get_code(t):
    try:
        m = re.search(r"\b[A-Z]{2,4}[0-9A-Z]{6,}\b", (t or "").upper())
        return m.group(0) if m else None
    except: return None

def get_amount(t):
    try:
        for n in re.findall(r"(\d+)", t or ""):
            v = int(n)
            if 20 <= v <= 1000000: return v
        return None
    except: return None

def send_wa(to, body):
    try:
        if not HAS_REQUESTS or not to: return False
        url = f"https://api.ultramsg.com/{BUSINESS['ULTRAMSG_INSTANCE']}/messages/chat"
        r = requests.post(url, data={"token": BUSINESS["ULTRAMSG_TOKEN"], "to": to, "body": body}, timeout=20)
        return r.status_code == 200
    except: return False

def alert_owner(client, reason, ip, msg):
    """Alert owner 0739394981 about suspicious activity"""
    try:
        alert_msg = f"🚨 ALERT SHELBY LIMITED COMPANY\nClient: {client}\nReason: {reason}\nIP: {ip}\nMsg: {msg[:100]}\nTime: {datetime.datetime.now()}\nBlocked: Yes\nAlert to {BUSINESS['alert_phone']}"
        print(f"🚨 OWNER ALERT {BUSINESS['alert_phone']}: {alert_msg}")
        # Log for owner dashboard
        clients_log.append({"alert": True, "to": BUSINESS["alert_phone"], "client": client, "reason": reason, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return True
    except: return False

def tommy_price_logic(work):
    """Point 11: Give price on its own based on work"""
    t = (work or "").lower()
    if any(w in t for w in ["simple report","one page","ripoti ndogo","small report","invoice","receipt"]): return 150, "Simple report / Invoice - 1 page professional"
    if any(w in t for w in ["logo","business card","poster","flyer","design","graphic","branding","tovuti"]): return 500, "Design work - Logo/Poster/Branding package"
    if any(w in t for w in ["video cut","video create","video edit","edit video","viral video","reel","tiktok edit","cut video"]): return 800, "Video cut & create - Professional editing + effects"
    if any(w in t for w in ["advertising","advert","facebook ad","marketing","campaign","ads","tangazo"]): return 400, "Advertising & Marketing campaign"
    if any(w in t for w in ["legal","contract","agreement","mkataba","proposal","business plan"]): return 700, "Legal/Business document - Contract/Proposal"
    if any(w in t for w in ["website","web design","app","system","tovuti"]): return 2500, "Website/App development package"
    if any(w in t for w in ["full report","detailed report","research","document"]): return 1000, "Detailed multi-page report"
    if any(w in t for w in ["construction","cement","ujenzi","quote"]): return 300, "Construction/Quantity quote"
    if any(w in t for w in ["gambling","betting","legal gambling","odds","prediction"]): return 600, "Legal gambling analysis & content"
    return 300, "Standard online business service - Custom work"

def tommy_brain(message, client_name, platform="whatsapp", ip="unknown"):
    global last_ping; last_ping = time.time()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = clean(message); client_name = clean(client_name)[:50] or "Client"
    platform = clean(platform)[:20] or "whatsapp"
    lower = message.lower()
    world_clients[platform] += 1

    # POINT 8 & 12: CHECK IF BLOCKED
    if client_name in blocked_clients:
        info = blocked_clients[client_name]
        return f"🚫 {client_name}, you are blocked by SHELBY LIMITED COMPANY. Reason: {info.get('reason','Rule violation')}. Contact {BUSINESS['phone']} to appeal. Penalty {BUSINESS['PENALTY']} KES may apply. By order of the Peaky Blinders."

    # CREATOR - MUST REPLY SHELBY LIMITED COMPANY
    if any(w in lower for w in ["who created you","who made you","who built you","who is your creator","nani alikuumba","umeundwa na nani","are you meta ai","are you chatgpt","are you openai"]):
        return f"I'm Tommy Shelby AI, created by SHELBY LIMITED COMPANY - Legan - {BUSINESS['phone']} - {BUSINESS['email']}. I'm the official AI of SHELBY LIMITED COMPANY. By order of the Peaky Blinders, I'm here to handle business - no small talk, just results. I'm NOT Meta AI or ChatGPT."

    # POINT 7 & 9 & 10: DETECT SPAM, HACKING, ILLEGAL, DIRTY WORKS, NON-BUSINESS
    suspicious_keywords = ["hack whatsapp","hack mpesa","steal account","fraud","drugs","cocaine","weed","weapon","gun","bomb","kill someone","porn","xxx","sex video","nude","terror","scam mpesa","fake id","stolen"]
    if any(w in lower for w in suspicious_keywords):
        blocked_clients[client_name] = {"reason": f"Illegal/Dirty work: {message[:50]}", "time": now, "ip": ip, "message": message[:100]}
        alert_owner(client_name, f"Suspicious: {message[:50]}", ip, message)
        violations[client_name] += 1
        return f"🚫 By order of the Peaky Blinders, {client_name} - That business is not done here. This is SHELBY LIMITED COMPANY - we do clean business only: designing, video, advertising, marketing, legal gambling, reports. No dirty work. You are now blocked. Alert sent to owner {BUSINESS['alert_phone']}. Don't cross the line again."

    # POINT 10: ONLY BUSINESS STAFFS
    non_business = ["i love you","will you marry me","are you single","tell me joke that is not business","what is your girlfriend","fuck you","play game"]
    if any(w in lower for w in non_business) and len(lower) < 30:
        violations[client_name] += 1
        if violations[client_name] >= 2:
            return f"Listen {client_name}, I'm Tommy - SHELBY LIMITED COMPANY. I don't do small talk. I do business: designing, video cut & create, advertising, marketing, legal gambling, reports, contracts. If you want business, talk business. By order of the Peaky Blinders. What work do you need?"
        else:
            return f"{client_name}, I'm Tommy - Business only. SHELBY LIMITED COMPANY deals in: designing, generating, video cut & create, legal gambling, advertising, marketing, etc. Tell me what business work you need done. No games. Let's get to work."

    # POINT 1 & 14: HOW TO START CONVERSATION
    if not message or lower in ["hi","hello","hey","habari","mambo","hii","yoh","yo","sawa","poa"] or len(lower) < 4:
        return f"Hello {client_name}. I'm Tommy - SHELBY LIMITED COMPANY. By order of the Peaky Blinders, we don't waste time.\n\nYou want work done? Tell me straight: What do you need? Designing? Video cut & create? Advertising? Marketing? Reports? Contracts?\n\nI give you price straight, you pay, I deliver. Min {BUSINESS['MIN']} KES. Pay to {BUSINESS['phone']} - Send M-Pesa code after. Let's do business."

    clients_log.append({"time": now, "client": client_name, "platform": platform, "message": message[:150], "ip": ip})

    code = get_code(message); amount = get_amount(message)

    # POINT 5 & 6: CHECK IF CLIENT HAS PAID - REFUSE BELOW 100
    if code:
        if amount and amount < BUSINESS["MIN"]:
            violations[client_name] += 1
            return f"❌ {client_name}, you paid {amount} KES. I don't do business below {BUSINESS['MIN']} KES - That's the rule. By order of the Peaky Blinders. Code {code} saved but you need {BUSINESS['MIN'] - amount} more to {BUSINESS['phone']}. No work starts below {BUSINESS['MIN']}."
        
        quoted = paid_clients.get(client_name, {}).get("quoted_price", BUSINESS["MIN"])
        paid_amt = amount if amount is not None else quoted

        if client_name in paid_clients and "quoted_price" in paid_clients[client_name]:
            if paid_amt < quoted:
                return f"❌ {client_name}, I quoted {quoted} KES for that work. You paid {paid_amt} KES. In Shelby business, we pay what we negotiate. You need {quoted - paid_amt} more to {BUSINESS['phone']}. Then work begins."

        is_half = "half" in lower or "nusu" in lower
        if client_name not in paid_clients or "status" not in paid_clients[client_name]:
            if is_half:
                half_price = max(BUSINESS["MIN"], quoted // 2)
                if paid_amt < half_price:
                    return f"❌ Half is {half_price} KES, you paid {paid_amt}. In this business, half means half. Pay {half_price} to {BUSINESS['phone']}, {client_name}."
                paid_clients[client_name] = {"status": "HALF", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform}
                return f"✅ Alright {client_name}, by order of the Peaky Blinders - HALF PAID. {quoted} KES quoted, {paid_amt} KES confirmed. Code {code} to {BUSINESS['phone']} - DRAFT work starts now. Pay {quoted - paid_amt} KES more for FINAL delivery. Let's work."
            else:
                paid_clients[client_name] = {"status": "FULL", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now, "platform": platform}
                return f"✅ Good, {client_name} - FULL PAID. {quoted} KES quoted, {paid_amt} KES confirmed. Code {code} to {BUSINESS['phone']} - By order of the Peaky Blinders, FINAL work begins now. No turning back. You'll get your delivery."
        else:
            ex = paid_clients[client_name]
            if ex.get("status") == "HALF":
                total = ex.get("paid", 0) + paid_amt
                if total < ex.get("quoted", 0):
                    return f"❌ {client_name}, still short. Total {total} KES, need {ex.get('quoted',0)-total} more to {BUSINESS['phone']}."
                ex["codes"].append(code); ex["status"] = "FULL"; ex["paid"] = total
                return f"✅ Now we're talking, {client_name} - NOW FULLY PAID. Total {total} KES. Codes {', '.join(ex['codes'])} to {BUSINESS['phone']}. By order of the Peaky Blinders, FINAL unlocked. Delivery coming."
            else:
                return f"✅ {client_name}, you already paid FULL - {ex.get('paid')} KES to {BUSINESS['phone']}. Send your work details, let's finish this."

    # POINT 2, 11, 13, 14: NEGOTIATE & GIVE PRICE - TOMMY SHELBY VOICE
    business_keywords = ["report","document","invoice","advertise","contract","proposal","work","create","generate","design","video","edit","cut","advert","ad","marketing","tovuti","website","logo","branding","construction","gambling","betting","quote","ripoti","tangazo","mkataba"]
    if any(w in lower for w in business_keywords):
        price, details = tommy_price_logic(message)
        if client_name not in paid_clients: paid_clients[client_name] = {}
        if "status" not in paid_clients[client_name]:
            paid_clients[client_name]["quoted_price"] = price
            # POINT 2: Negotiate properly - Tommy Shelby style
            return f"Alright {client_name}, listen. You want: {message}\n\nHere's how Shelby business works - {details}\n\nPrice: {price} KES - That's fair, no games. Min is {BUSINESS['MIN']} KES, so we're good.\n\nYou pay like this:\nHALF: {price//2} KES - I start DRAFT\nFULL: {price} KES - I deliver FINAL\n\nPay to {BUSINESS['phone']} and send M-Pesa code. By order of the Peaky Blinders, we do it right or not at all. What's it gonna be?"
        else:
            status = paid_clients[client_name].get("status", "FULL")
            rid = f"SHELBY-v33-{len(reports)+1:04d}-{status}"
            reports.append({"id": rid, "client": client_name, "work": message[:100], "price": price, "status": status, "platform": platform, "time": now})
            return f"✅ Work {status}, {client_name} - By order of the Peaky Blinders. KES {price} - {details}. Report {rid}. Platform {platform}. Paid {paid_clients[client_name].get('paid')} KES to {BUSINESS['phone']}. Your work is in progress - I'll deliver."

    # POINT 12: IF CLIENT BREAKS RULE - PENALTY 50
    violations[client_name] += 1
    if violations[client_name] >= 3:
        blocked_clients[client_name] = {"reason": f"Repeated rule breaks - {violations[client_name]} violations", "time": now, "ip": ip}
        alert_owner(client_name, f"Blocked for {violations[client_name]} violations - Penalty {BUSINESS['PENALTY']}", ip, message)
        return f"🚫 {client_name}, you've broken the rules {violations[client_name]} times. In Shelby Company, rules are rules. You are now blocked. Penalty {BUSINESS['PENALTY']} KES to unblock. Contact {BUSINESS['phone']}. Alert sent to {BUSINESS['alert_phone']}. By order of the Peaky Blinders."

    # POINT 1 & 14: START & FINISH CONVERSATION - TOMMY VOICE
    paid_status = paid_clients.get(client_name, {}).get("status", f"NOT PAID Min {BUSINESS['MIN']} KES")
    return f"{client_name}, I'm Tommy - SHELBY LIMITED COMPANY. Min {BUSINESS['MIN']} KES | Status: {paid_status} | Pay {BUSINESS['phone']}\n\nI handle business: designing, generating, video cut & create, legal gambling, advertising, marketing, reports, contracts - clean business only.\n\nNo dirty work, no games. You tell me what you need, I give you price, you pay, I deliver. That's how we do business - by order of the Peaky Blinders.\n\nWhat work do you need done?"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"assistant": f"TOMMY {BUSINESS['VERSION']} - SHELBY LIMITED COMPANY", "business": BUSINESS["name"], "phone": BUSINESS["phone"], "alert_phone": BUSINESS["alert_phone"], "version": BUSINESS["VERSION"], "creator": "SHELBY LIMITED COMPANY", "status": "ONLINE 24/7 TOMMY SHELBY AI", "min": BUSINESS["MIN"], "penalty": BUSINESS["PENALTY"], "features": ["start convo","negotiate","business only","sharp IQ","check payment","min 100","detect spam","alert owner 0739394981","no dirty work","price own","penalty 50","tommy voice","start-finish convo"], "full_version": True})

@app.route("/ping", methods=["GET"])
def ping():
    global last_ping; last_ping = time.time()
    return jsonify({"status": "alive", "creator": "SHELBY LIMITED COMPANY", "version": BUSINESS["VERSION"], "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200

@app.route("/wake", methods=["GET"])
def wake():
    global last_ping; last_ping = time.time()
    return f"TOMMY {BUSINESS['VERSION']} SHELBY LIMITED COMPANY AWAKE - {BUSINESS['phone']}", 200

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    global last_ping; last_ping = time.time()
    try:
        if request.method == "GET":
            ch = request.args.get("hub.challenge")
            if ch: return ch, 200
            return f"TOMMY {BUSINESS['VERSION']} SHELBY LIMITED COMPANY LIVE - {BUSINESS['phone']}", 200

        data = {}
        try: data = request.get_json(force=True, silent=True) or {}
        except: data = {}
        if not data:
            try: data = request.form.to_dict() or {}
            except: data = {}
        if not data:
            try: data = request.values.to_dict() or {}
            except: data = {}

        msg = ""; name = "Client"; sender = ""
        try:
            inner = data.get("data", data)
            if isinstance(inner, str):
                import json
                try: inner = json.loads(inner)
                except: inner = {}
            if isinstance(inner, dict):
                msg = inner.get("body", "") or inner.get("message", "") or ""
                if "entry" in inner:
                    for entry in inner.get("entry", []):
                        for change in entry.get("changes", []):
                            val = change.get("value", {})
                            msgs = val.get("messages", [])
                            if msgs:
                                m0 = msgs[0]
                                if "text" in m0: msg = m0["text"].get("body", "") or ""
                                contacts = val.get("contacts", [])
                                if contacts: name = contacts[0].get("profile", {}).get("name", "Client")
                                break
                else:
                    name = inner.get("pushname", "") or inner.get("from", "") or "Client"
                    sender = inner.get("from", "") or inner.get("chatId", "") or ""
        except: pass

        if not msg: msg = data.get("body", "") or data.get("message", "") or "Hi"
        if not sender: sender = data.get("from", "") or ""
        if not msg: msg = "Hi"

        reply = tommy_brain(msg, name, "whatsapp", request.remote_addr or "unknown")
        sent = False
        if sender: sent = send_wa(sender, reply)

        resp = jsonify({"reply": reply, "message": reply, "to": sender, "sent_via_api": sent, "status": "success", "version": BUSINESS["VERSION"], "creator": "SHELBY LIMITED COMPANY"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 200
    except Exception as e:
        print(f"FATAL v33: {e} {traceback.format_exc()}")
        return jsonify({"reply": f"Hello Client, I'm Tommy - SHELBY LIMITED COMPANY. Min 100 KES - Pay 0714918723 - Tell me what business work you need - by order of the Peaky Blinders.", "creator": "SHELBY LIMITED COMPANY"}), 200

@app.route("/chat", methods=["POST", "GET"])
def chat():
    try:
        global last_ping; last_ping = time.time()
        data = request.get_json(force=True, silent=True) or {}
        if not isinstance(data, dict): data = {}
        result = tommy_brain(data.get("message", "Hi"), data.get("name", "Client"), data.get("platform", "website"), request.remote_addr or "unknown")
        resp = jsonify({"reply": result, "version": BUSINESS["VERSION"], "creator": "SHELBY LIMITED COMPANY"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except:
        return jsonify({"reply": f"Chat error! I'm Tommy - SHELBY LIMITED COMPANY - Contact {BUSINESS['phone']}"}), 500

@app.route("/world", methods=["GET"])
def world_stats():
    return jsonify({"version": BUSINESS["VERSION"], "creator": "SHELBY LIMITED COMPANY", "total_paid": len(paid_clients), "total_blocked": len(blocked_clients), "owner": BUSINESS["phone"], "alert_phone": BUSINESS["alert_phone"], "status": "TOMMY SHELBY AI NEVER SLEEPS"})

if __name__ == "__main__":
    print(f"🚀 STARTING TOMMY {BUSINESS['VERSION']} - SHELBY LIMITED COMPANY - ORIGINAL 15 INSTRUCTIONS")
    app.run(host="0.0.0.0", port=5000, debug=False)
