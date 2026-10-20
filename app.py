from flask import Flask, request, jsonify
import datetime, re, time, threading, random, json
from collections import defaultdict

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

app = Flask(__name__)

BUSINESS = {
    "name": "Shelby limited company",
    "legal_name": "SHELBY LIMITED COMPANY",
    "creator": "Shelby limited company",
    "owner": "Legan Shelby",
    "phone": "0739394981",
    "phone_formatted": "254739394981",
    "email": "leganshelby50@gmail.com",
    "instagram": "Shelby limited company",
    "facebook": "Shelby limited company",
    "every_platform": "Shelby limited company",
    "MIN": 100,
    "PENALTY": 50,
    "VERSION": "v38 FINAL NO ERROR",
    "URL": "https://shelby-tommy-uh.onrender.com",
    "ULTRAMSG_INSTANCE": "instance194905",
    "ULTRAMSG_TOKEN": "4micq16wz3a5yd8b"
}

paid_clients = {}
reports = []
clients_log = []
world_clients = defaultdict(int)
blocked_clients = {}
violations = defaultdict(int)
last_reply = {}
last_ping = time.time()

def keep_alive():
    global last_ping
    while True:
        try:
            time.sleep(240)
            last_ping = time.time()
            if HAS_REQUESTS:
                try:
                    requests.get(f"{BUSINESS['URL']}/ping", timeout=8)
                except:
                    pass
        except:
            time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()

def clean(t):
    if not t or not isinstance(t, str):
        return ""
    return re.sub(r"<[^>]*>", "", t)[:2000].strip()

def get_code(t):
    try:
        m = re.search(r"\b[A-Z]{2,4}[0-9A-Z]{6,}\b", (t or "").upper())
        return m.group(0) if m else None
    except:
        return None

def get_amount(t):
    try:
        for n in re.findall(r"(\d+)", t or ""):
            v = int(n)
            if 20 <= v <= 1000000:
                return v
        return None
    except:
        return None

def send_wa(to, body):
    try:
        if not to or not HAS_REQUESTS:
            return False
        if to.startswith("07"):
            to = "254" + to[1:]
        url = f"https://api.ultramsg.com/{BUSINESS['ULTRAMSG_INSTANCE']}/messages/chat"
        r = requests.post(url, data={"token": BUSINESS["ULTRAMSG_TOKEN"], "to": to, "body": body}, timeout=20)
        return r.status_code == 200
    except:
        return False

def is_owner(num):
    if not num:
        return False
    return "739394981" in str(num)

def alert_block(client, reason, ip, msg, attempts=1):
    try:
        alert = f"BLOCK v38 Client:{client} Reason:{reason} IP:{ip} Msg:{msg[:80]} Time:{datetime.datetime.now().strftime('%H:%M')} Owner:{BUSINESS['owner']} Email:{BUSINESS['email']} Reply UNBLOCK {client} REPORT {client} SEARCH {client}"
        send_wa(BUSINESS["phone_formatted"], alert)
    except:
        pass

def search_customers(query):
    q = (query or "").lower().strip()
    results = {"paid": [], "blocked": [], "logs": [], "reports": []}
    if not q or len(q) < 2:
        return results
    try:
        for name, data in paid_clients.items():
            if q in name.lower():
                results["paid"].append({name: data})
        for name, data in blocked_clients.items():
            if q in name.lower():
                results["blocked"].append({name: data})
        for log in clients_log[-50:]:
            if q in str(log).lower():
                results["logs"].append(log)
        for rep in reports[-20:]:
            if q in str(rep).lower():
                results["reports"].append(rep)
    except:
        pass
    return results

def price_logic(work):
    try:
        t = (work or "").lower()
        if "report" in t or "invoice" in t:
            return 150, "Simple report"
        if "logo" in t or "poster" in t or "design" in t:
            return 500, "Design work"
        if "video" in t:
            return 800, "Video cut & create"
        if "advert" in t or "marketing" in t:
            return 400, "Advertising"
        if "contract" in t or "mkataba" in t:
            return 700, "Legal document"
        if "website" in t or "app" in t:
            return 2500, "Website/App"
        return 300, "Standard business service"
    except:
        return 300, "Standard business service"

def tommy_brain(message, client_name, platform, sender_number, ip):
    global last_ping, last_reply
    try:
        last_ping = time.time()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        message = clean(message)
        client_name = clean(client_name)[:50] or "Client"
        lower = message.lower()
        world_clients[platform] += 1

        try:
            clients_log.append({"time": now, "client": client_name, "platform": platform, "message": message[:100], "ip": ip})
            if len(clients_log) > 200:
                clients_log.pop(0)
        except:
            pass

        # Creator / Owner - ALWAYS WORKS
        creator_keys = ["who created you", "who made you", "are you meta", "are you chatgpt", "who owns you", "owner", "creator", "who built you", "nani alikuumba"]
        if any(w in lower for w in creator_keys):
            if client_name not in blocked_clients or is_owner(sender_number):
                return f"I'm Tommy, built by {BUSINESS['creator']}. Company: {BUSINESS['creator']} Owner: {BUSINESS['owner']} Email: {BUSINESS['email']} WhatsApp: {BUSINESS['phone']} IG/FB: {BUSINESS['every_platform']}"

        # Owner commands
        if is_owner(sender_number):
            if lower.startswith("search "):
                q = lower.replace("search", "").strip()
                if not q:
                    return "Usage: SEARCH name"
                res = search_customers(q)
                total = len(res["paid"]) + len(res["blocked"]) + len(res["logs"]) + len(res["reports"])
                if total == 0:
                    return f"SEARCH '{q}' No results. Paid:{len(paid_clients)} Blocked:{len(blocked_clients)}"
                return f"SEARCH '{q}' Found {total} Paid:{len(res['paid'])} Blocked:{len(res['blocked'])} Logs:{len(res['logs'])}"

            if lower.startswith("unblock "):
                target = lower.replace("unblock", "").strip().split()[0] if lower.replace("unblock", "").strip() else ""
                if not target:
                    return "Usage: UNBLOCK name"
                found = None
                for k in list(blocked_clients.keys()):
                    if target.lower() in k.lower():
                        found = k
                        break
                if not found:
                    found = target
                if found in blocked_clients:
                    del blocked_clients[found]
                    if found in violations:
                        violations[found] = 0
                    return f"UNBLOCKED {found} by owner {BUSINESS['owner']}"
                return f"{target} not blocked"

            if lower.startswith("report "):
                target = lower.replace("report", "").strip().split()[0] if lower.replace("report", "").strip() else ""
                found = None
                for k in list(blocked_clients.keys()):
                    if target.lower() in k.lower():
                        found = k
                        break
                if found and found in blocked_clients:
                    blocked_clients[found]["reported"] = True
                    return f"REPORTED {found} and kept BLOCKED"
                return f"{target} not found"

            if "list blocked" in lower:
                if not blocked_clients:
                    return f"No blocked clients. {BUSINESS['creator']} Owner {BUSINESS['owner']}"
                lst = "\n".join([f"- {k}" for k in list(blocked_clients.keys())[:20]])
                return f"BLOCKED {len(blocked_clients)}:\n{lst}"

            if "update yourself" in lower or lower == "update":
                BUSINESS["VERSION"] = f"v38 UPDATED {datetime.datetime.now().strftime('%H:%M')}"
                return f"UPDATED to {BUSINESS['VERSION']} Owner {BUSINESS['owner']} Creator {BUSINESS['creator']}"

            if "contacts" in lower:
                return f"CONTACTS Company:{BUSINESS['creator']} Owner:{BUSINESS['owner']} Email:{BUSINESS['email']} WhatsApp:{BUSINESS['phone']} IG:{BUSINESS['instagram']} FB:{BUSINESS['facebook']} Every:{BUSINESS['every_platform']}"

        # Blocked check
        if client_name in blocked_clients:
            try:
                blocked_clients[client_name]["attempts"] = blocked_clients[client_name].get("attempts", 1) + 1
                if blocked_clients[client_name]["attempts"] % 5 == 0:
                    alert_block(client_name, blocked_clients[client_name].get("reason", ""), ip, message, blocked_clients[client_name]["attempts"])
            except:
                pass
            return None

        # Dirty check
        dirty = ["pornography", "xxx porn", "sex video", "nude photo", "cocaine", "weed drugs", "hack whatsapp", "hack mpesa", "steal mpesa", "weapon gun", "bomb make", "send to me porn"]
        if any(w in lower for w in dirty):
            try:
                violations[client_name] += 1
            except:
                violations[client_name] = 1
            if violations[client_name] == 1:
                alert_block(client_name, f"WARNING {message[:40]}", ip, message, 1)
                return f"{client_name}, I don't do that work. I'm Tommy from {BUSINESS['creator']} Owner {BUSINESS['owner']} clean business only. First warning. Min {BUSINESS['MIN']} KES. Contact {BUSINESS['phone']}"
            else:
                blocked_clients[client_name] = {"reason": f"Dirty {message[:50]}", "time": now, "ip": ip, "attempts": 1}
                alert_block(client_name, f"BLOCK {message[:50]}", ip, message, 1)
                return f"BLOCKED {client_name}. Owner {BUSINESS['owner']} {BUSINESS['phone']} Reply UNBLOCK {client_name} or REPORT {client_name}"

        # Greetings - NO REPETITION
        if not message or lower in ["hi", "hello", "hey", "habari", "mambo"] or len(lower) < 4:
            g1 = f"Hey {client_name}, I'm Tommy from {BUSINESS['creator']} Owner {BUSINESS['owner']}. What business? Designing, video cut, advertising, marketing, reports. Min {BUSINESS['MIN']} KES pay {BUSINESS['phone']} Email {BUSINESS['email']}"
            g2 = f"Hello {client_name}. Tommy here {BUSINESS['creator']} Owner {BUSINESS['owner']}. You need work? Design video marketing report? I price it. WhatsApp {BUSINESS['phone']}"
            g3 = f"Hi {client_name}, welcome to {BUSINESS['creator']}. I'm Tommy. What work? Logo Video Ad? Tell me I price you pay via M-Pesa code I deliver. Contact {BUSINESS['email']}"
            greetings = [g1, g2, g3]
            last = last_reply.get(client_name)
            avail = [g for g in greetings if g != last]
            if not avail:
                avail = greetings
            chosen = random.choice(avail)
            last_reply[client_name] = chosen
            return chosen

        # Payment
        code = get_code(message)
        amount = get_amount(message)
        if code:
            if amount and amount < BUSINESS["MIN"]:
                return f"{client_name} code {code} but {amount} KES below min {BUSINESS['MIN']} KES Add {BUSINESS['MIN']-amount} to {BUSINESS['phone']}"
            quoted = paid_clients.get(client_name, {}).get("quoted_price", BUSINESS["MIN"])
            paid_amt = amount if amount is not None else quoted
            if client_name in paid_clients and "quoted_price" in paid_clients[client_name] and paid_amt < quoted:
                return f"{client_name} we agreed {quoted} KES you sent {paid_amt} KES Need {quoted-paid_amt} more to {BUSINESS['phone']}"
            is_half = "half" in lower or "nusu" in lower
            if client_name not in paid_clients or "status" not in paid_clients[client_name]:
                if is_half:
                    half_price = max(BUSINESS["MIN"], quoted // 2)
                    if paid_amt < half_price:
                        return f"Half is {half_price} KES you paid {paid_amt}"
                    paid_clients[client_name] = {"status": "HALF", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now}
                    return f"HALF paid {client_name} {paid_amt} KES Code {code} to {BUSINESS['phone']} DRAFT starts Pay {quoted-paid_amt} more for FINAL {BUSINESS['creator']}"
                else:
                    paid_clients[client_name] = {"status": "FULL", "codes": [code], "paid": paid_amt, "quoted": quoted, "time": now}
                    return f"FULL paid {client_name} {paid_amt} KES Code {code} to {BUSINESS['phone']} Work starts now {BUSINESS['creator']}"
            else:
                ex = paid_clients[client_name]
                if ex.get("status") == "HALF":
                    total = ex.get("paid", 0) + paid_amt
                    if total < ex.get("quoted", 0):
                        return f"Total {total} KES need {ex.get('quoted',0)-total} more"
                    ex["codes"].append(code)
                    ex["status"] = "FULL"
                    ex["paid"] = total
                    return f"Now FULLY PAID {client_name} Total {total} KES FINAL unlocked {BUSINESS['creator']}"
                else:
                    return f"{client_name} already fully paid {ex.get('paid')} KES"

        # Business work
        keys = ["report", "document", "invoice", "advertise", "contract", "work", "create", "design", "video", "edit", "advert", "marketing", "website", "logo", "quote", "ripoti", "tangazo"]
        if any(w in lower for w in keys):
            price, details = price_logic(message)
            if client_name not in paid_clients:
                paid_clients[client_name] = {}
            if "status" not in paid_clients[client_name]:
                paid_clients[client_name]["quoted_price"] = price
                return f"{client_name} got it {message} {details} {price} KES Pay HALF {price//2} or FULL {price} to {BUSINESS['phone']} then send code {BUSINESS['creator']} Owner {BUSINESS['owner']}"
            else:
                rid = f"SHELBY-v38-{len(reports)+1:04d}"
                reports.append({"id": rid, "client": client_name, "work": message[:80], "price": price, "time": now})
                return f"Working {client_name} KES {price} {details} Report {rid} Paid {paid_clients[client_name].get('paid')} KES {BUSINESS['creator']}"

        return f"{client_name} I handle designing video cut advertising marketing reports contracts Min {BUSINESS['MIN']} KES Pay to {BUSINESS['phone']} {BUSINESS['creator']} Owner {BUSINESS['owner']} Email {BUSINESS['email']} IG {BUSINESS['every_platform']}"

    except Exception as e:
        return f"Hey {client_name} I'm Tommy from {BUSINESS['creator']} Owner {BUSINESS['owner']} What business? Min {BUSINESS['MIN']} KES pay to {BUSINESS['phone']} Email {BUSINESS['email']}"

@app.route("/", methods=["GET"])
def home():
    try:
        return jsonify({
            "assistant": BUSINESS["VERSION"],
            "creator": BUSINESS["creator"],
            "owner": BUSINESS["owner"],
            "email": BUSINESS["email"],
            "whatsapp": BUSINESS["phone"],
            "every_platform": BUSINESS["every_platform"],
            "status": "ONLINE NO ERROR",
            "blocked": len(blocked_clients),
            "paid": len(paid_clients)
        })
    except:
        return jsonify({"status": "alive"}), 200

@app.route("/ping", methods=["GET"])
def ping():
    global last_ping
    last_ping = time.time()
    return jsonify({"status": "alive", "version": BUSINESS["VERSION"], "creator": BUSINESS["creator"], "owner": BUSINESS["owner"]}), 200

@app.route("/search/<query>", methods=["GET"])
def search_route(query):
    try:
        res = search_customers(query)
        return jsonify({"query": query, "results": res}), 200
    except:
        return jsonify({"query": query, "results": {}}), 200

@app.route("/update", methods=["GET", "POST"])
def update_route():
    try:
        BUSINESS["VERSION"] = f"v38 SELF-UPDATED {datetime.datetime.now().strftime('%H:%M:%S')}"
        return jsonify({"status": "updated", "version": BUSINESS["VERSION"]}), 200
    except:
        return jsonify({"status": "updated"}), 200

@app.route("/contacts", methods=["GET"])
def contacts_route():
    try:
        return jsonify({
            "creator": BUSINESS["creator"],
            "owner": BUSINESS["owner"],
            "email": BUSINESS["email"],
            "whatsapp": BUSINESS["phone"],
            "instagram": BUSINESS["instagram"],
            "facebook": BUSINESS["facebook"],
            "every_platform": BUSINESS["every_platform"]
        }), 200
    except:
        return jsonify({}), 200

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    global last_ping
    last_ping = time.time()
    try:
        if request.method == "GET":
            ch = request.args.get("hub.challenge")
            if ch:
                return ch, 200
            return f"TOMMY {BUSINESS['VERSION']} LIVE {BUSINESS['creator']} Owner {BUSINESS['owner']}", 200

        data = {}
        try:
            data = request.get_json(force=True, silent=True) or {}
        except:
            data = {}
        if not data:
            try:
                data = request.form.to_dict() or {}
            except:
                data = {}

        msg = ""
        name = "Client"
        sender = ""
        sender_num = ""

        try:
            inner = data.get("data", data)
            if isinstance(inner, dict):
                msg = inner.get("body", "") or inner.get("message", "") or ""
                name = inner.get("pushname", "") or inner.get("from", "") or "Client"
                sender = inner.get("from", "") or inner.get("chatId", "") or ""
                sender_num = sender
                if "entry" in inner:
                    for entry in inner.get("entry", []):
                        for change in entry.get("changes", []):
                            val = change.get("value", {})
                            msgs = val.get("messages", [])
                            if msgs:
                                m0 = msgs[0]
                                if "text" in m0:
                                    msg = m0["text"].get("body", "") or ""
                                contacts = val.get("contacts", [])
                                if contacts:
                                    name = contacts[0].get("profile", {}).get("name", "Client")
                                if msgs[0].get("from"):
                                    sender_num = msgs[0].get("from")
        except:
            pass

        if not msg:
            msg = data.get("body", "") or data.get("message", "") or "Hi"
        if not sender:
            sender = data.get("from", "") or ""
        if not sender_num:
            sender_num = sender

        reply = tommy_brain(msg, name, "whatsapp", sender_num, request.remote_addr or "unknown")
        if reply is None:
            return jsonify({"reply": None, "status": "blocked_silent", "blocked": True}), 200

        sent = False
        if sender:
            sent = send_wa(sender, reply)

        return jsonify({"reply": reply, "to": sender, "sent": sent, "version": BUSINESS["VERSION"], "creator": BUSINESS["creator"], "owner": BUSINESS["owner"]}), 200

    except Exception as e:
        return jsonify({"reply": f"Hey I'm Tommy from Shelby limited company Owner Legan Shelby Min 100 KES pay 0739394981", "status": "error handled"}), 200

@app.route("/unblock/<client>", methods=["GET"])
def unblock_client(client):
    try:
        if client in blocked_clients:
            del blocked_clients[client]
            if client in violations:
                violations[client] = 0
            return jsonify({"status": f"{client} unblocked"}), 200
        return jsonify({"status": f"{client} not blocked", "blocked": list(blocked_clients.keys())}), 200
    except:
        return jsonify({"status": "done"}), 200

@app.route("/blocked", methods=["GET"])
def list_blocked():
    try:
        return jsonify({"blocked": blocked_clients, "count": len(blocked_clients), "creator": BUSINESS["creator"], "owner": BUSINESS["owner"]}), 200
    except:
        return jsonify({"blocked": {}, "count": 0}), 200

if __name__ == "__main__":
    print(f"STARTING TOMMY {BUSINESS['VERSION']} {BUSINESS['creator']} Owner {BUSINESS['owner']}")
    app.run(host="0.0.0.0", port=5000, debug=False)
