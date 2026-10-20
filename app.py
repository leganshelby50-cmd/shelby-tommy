from flask import Flask, request, jsonify
import datetime, re, time, logging, requests
from collections import defaultdict

app = Flask(__name__)

BUSINESS={"name":"SHELBY LIMITED","phone":"0714918723","email":"leganshelby50@gmail.com","MIN":150}
ULTRAMSG_INSTANCE_ID="YOUR_INSTANCE_ID_HERE"
ULTRAMSG_TOKEN="YOUR_TOKEN_HERE"

paid_clients={}
reports=[]
blocked_ips={}
request_counts=defaultdict(list)
world_clients=defaultdict(int)

def is_blocked(ip):
    if ip in blocked_ips:
        if time.time()-blocked_ips[ip]<300: return True
        del blocked_ips[ip]
    return False

def check_rate_limit(ip):
    now=time.time()
    request_counts[ip]=[t for t in request_counts[ip] if now-t<60]
    request_counts[ip].append(now)
    if len(request_counts[ip])>30:
        blocked_ips[ip]=now
        return False
    return True

def sanitize_input(text):
    if not text or not isinstance(text,str): return ""
    text=text[:2000]
    text=re.sub(r"<[^>]*>","",text)
    return text.strip()

def tommy_decide_price(work_text):
    t=(work_text or "").lower()
    if any(w in t for w in ["simple report","small report"]): return 150,"Simple report"
    if any(w in t for w in ["invoice","receipt"]): return 150,"Invoice"
    if any(w in t for w in ["advertise","facebook"]): return 300,"Ad post"
    if any(w in t for w in ["contract","agreement"]): return 500,"Contract"
    if any(w in t for w in ["proposal"]): return 700,"Proposal"
    if any(w in t for w in ["full report","detailed"]): return 800,"Detailed report"
    if any(w in t for w in ["campaign"]): return 1500,"Campaign"
    if any(w in t for w in ["website","logo","branding"]): return 2500,"Website/Branding"
    return 150,"Standard"

def get_code(text):
    m=re.search(r"\b[A-Z]{2,4}[0-9A-Z]{6,}\b",(text or "").upper())
    return m.group(0) if m else None

def get_amount(text):
    for n in re.findall(r"(\d+)",text or ""):
        v=int(n)
        if 50<=v<=1000000: return v
    return None

def tommy_brain(message,client_name,platform="website"):
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    message=sanitize_input(message)
    client_name=sanitize_input(client_name)[:50] or "Client"
    lower=message.lower()
    world_clients[platform]+=1
    if len(message)==0:
        return {"reply":f"Hello {client_name}! Tommy | Min 150 KES | Pay 0714918723"}
    code=get_code(message)
    amount=get_amount(message)
    if code:
        quoted=paid_clients.get(client_name,{}).get("quoted_price",150)
        paid_amt=amount if amount else quoted
        if amount and amount<150:
            return {"reply":f"{client_name}, {amount} KES too low! Min 150! Need {150-amount} more to 0714918723!"}
        is_half="half" in lower or "nusu" in lower
        if client_name not in paid_clients or "status" not in paid_clients[client_name]:
            if is_half:
                half_price=max(150,quoted//2)
                if paid_amt<half_price:
                    return {"reply":f"Half too low! Quoted {quoted}, half {half_price}. Paid {paid_amt}. Pay {half_price} to 0714918723!"}
                paid_clients[client_name]={"status":"HALF","codes":[code],"paid":paid_amt,"quoted":quoted,"time":now,"platform":platform}
                return {"reply":f"HALF PAID - {quoted} KES quoted, {paid_amt} paid! Code {code} to 0714918723! DRAFT started! Pay {quoted-paid_amt} for FINAL!"}
            else:
                paid_clients[client_name]={"status":"FULL","codes":[code],"paid":paid_amt,"quoted":quoted,"time":now,"platform":platform}
                return {"reply":f"FULL PAID - {quoted} KES quoted, {paid_amt} paid! Code {code} to 0714918723! FINAL work now!"}
        else:
            ex=paid_clients[client_name]
            if ex["status"]=="HALF":
                total=ex["paid"]+paid_amt
                if total<ex["quoted"]:
                    return {"reply":f"Still low! Total {total}, need {ex['quoted']-total} more to 0714918723!"}
                ex["codes"].append(code)
                ex["status"]="FULL"
                ex["paid"]=total
                return {"reply":f"NOW FULLY PAID! Total {total} KES! Codes {', '.join(ex['codes'])} to 0714918723. FINAL unlocked!"}
            else:
                return {"reply":f"Already FULLY PAID {client_name}! Paid {ex['paid']} to 0714918723! Tell work now!"}
    work_keys=["report","document","invoice","advertise","contract","proposal","work","create","website","logo"]
    if any(w in lower for w in work_keys):
        price,details=tommy_decide_price(message)
        if client_name not in paid_clients: paid_clients[client_name]={}
        if "status" not in paid_clients[client_name]:
            paid_clients[client_name]["quoted_price"]=price
            return {"reply":f"TOMMY QUOTE\nHi {client_name}! Work: {message}\nDetails: {details}\nPrice KES {price}\nMin 150\nPAY to 0714918723:\nHALF {price//2}\nFULL {price}","quoted_price":price}
        else:
            status=paid_clients[client_name]["status"]
            rid=f"SHELBY-{len(reports)+1:04d}-{status}"
            reports.append({"id":rid,"client":client_name,"work":message[:100],"price":price,"status":status,"time":now})
            return {"reply":f"WORK {status} - KES {price} ({details})! Report {rid} | Paid {paid_clients[client_name].get('paid')} to 0714918723"}
    if any(w in lower for w in ["price","bei","cost","quote"]):
        price,details=tommy_decide_price(message)
        if client_name not in paid_clients: paid_clients[client_name]={}
        paid_clients[client_name]["quoted_price"]=price
        return {"reply":f"QUOTE: {message} -> KES {price} ({details}) | Min 150 | Pay half {price//2} or full {price} to 0714918723!","quoted_price":price}
    paid_status=paid_clients.get(client_name,{}).get("status","NOT PAID Min 150 KES")
    return {"reply":f"Hi {client_name}! Tommy SHELBY LIMITED! Min 150 KES | Status {paid_status} | Pay 0714918723 | 24/7 Worldwide"}

def send_ultramsg_reply(to,msg):
    try:
        if "YOUR_" in ULTRAMSG_INSTANCE_ID: return False
        url=f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
        requests.post(url,data={"token":ULTRAMSG_TOKEN,"to":to,"body":msg},timeout=10)
        return True
    except: return False

@app.route("/",methods=["GET"])
def home():
    return jsonify({"assistant":"TOMMY ULTRAMSG","business":"SHELBY LIMITED","phone":"0714918723","status":"ONLINE","paid":len(paid_clients)})

@app.route("/chat",methods=["POST","GET"])
def chat():
    ip=request.remote_addr or "unknown"
    if is_blocked(ip): return jsonify({"reply":"Blocked"}),429
    if not check_rate_limit(ip): return jsonify({"reply":"Rate limit"}),429
    data=request.get_json(silent=True) or {}
    msg=sanitize_input(data.get("message","Hello"))
    name=sanitize_input(data.get("name","Client"))
    plat=sanitize_input(data.get("platform","website"))
    return jsonify(tommy_brain(msg,name,plat))

@app.route("/webhook",methods=["POST","GET"])
def webhook():
    if request.method=="GET":
        return "TOMMY ULTRAMSG LIVE - SHELBY LIMITED - 0714918723",200
    ip=request.remote_addr or "unknown"
    if is_blocked(ip): return jsonify({"error":"blocked"}),429
    if not check_rate_limit(ip): return jsonify({"error":"rate"}),429
    data=request.get_json(silent=True) or {}
    msg="";name="Client";phone=None;plat="whatsapp"
    if "data" in data:
        d=data["data"]
        msg=d.get("body","")
        phone=d.get("from","")
        name=d.get("pushname","") or phone
    if not msg:
        msg=sanitize_input(data.get("message","") or data.get("body","Hello"))
        name=sanitize_input(data.get("name","Client"))
    if not msg: return jsonify({"reply":"No message"}),200
    res=tommy_brain(msg,name,plat)
    if phone: send_ultramsg_reply(phone,res.get("reply",""))
    r=jsonify(res)
    r.headers["Access-Control-Allow-Origin"]="*"
    return r

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)
