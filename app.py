from flask import Flask, request
import requests
import time
import random
import os
from datetime import datetime

app = Flask(__name__)

# ULTRAMSG - DO NOT CHANGE
INSTANCE_ID = "instance194905"
TOKEN = "4micq16wz3a5yd8b"

# BUSINESS INFO
BOSS_NUMBER = "254714918723"
BUSINESS_NAME = "Legan Enterprises"
MPESA = "0714918723"
LOCATION = "Thika, Nairobi delivery available"

# --- TERMS & CONDITIONS - TOMMY KNOWS THIS LIKE CHATGPT ---
TERMS_AND_CONDITIONS = """
LEGAN ENTERPRISES TERMS & CONDITIONS - Tommy Bot Knows This:

1. PAYMENT: Lipa na M-Pesa 0714918723. Pay before delivery. Send M-Pesa code for confirmation.
2. DELIVERY: Nairobi KSh 200 (same day), Thika KSh 150, Outside Nairobi KSh 300 (24hrs). Free delivery for orders above KSh 10,000.
3. SIZES: Mens 46-60, Shoes 39-45, Kids 2-12 years. Exchange available if size wrong within 24hrs.
4. RETURNS: No return after wearing. Check before paying rider.
5. QUALITY: Original, quality thrift & new. Peaky Blinders style guaranteed.
6. ORDERS: Send Size + Product + Location + Phone. We confirm.
7. WORKING HOURS: Tommy replies 24/7, human delivery 8am-8pm.
8. WARRANTY: Shoes 2 weeks sole warranty.
"""

# PRODUCT DATABASE - For AI Discovery
PRODUCTS_DB = {
    "blazers": {"price": "4,500", "sizes": "46-60", "colors": "Black, Navy, Grey, Brown", "for": "Office, Wedding, Church, Official"},
    "coats": {"price": "5,500", "sizes": "M-3XL", "colors": "Black, Grey, Camel", "for": "Cold season, Official, Classy look"},
    "suits": {"price": "7,000", "sizes": "46-60", "colors": "Black, Navy, Grey", "for": "Wedding, Office, Ruracio, Interview"},
    "shoes_formal": {"price": "3,500", "sizes": "39-45", "colors": "Black, Brown", "for": "Office, Wedding"},
    "boots": {"price": "4,000", "sizes": "40-45", "colors": "Black, Brown", "for": "Casual, Hiking, Peaky style"},
    "sneakers": {"price": "2,800", "sizes": "40-44", "colors": "White, Black, Grey", "for": "Casual, Everyday"},
    "kids_suits": {"price": "2,500", "sizes": "2-12 years", "colors": "Black, Navy", "for": "Wedding, Church, School event"}
}

# SIMPLE MEMORY FOR DISCOVERY - Like ChatGPT
user_memory = {}

def send_whatsapp(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    data = {"token": TOKEN, "to": to, "body": message}
    try:
        time.sleep(random.uniform(1.2, 3.5)) # Human typing
        requests.post(url, data=data, timeout=15)
    except: pass

def send_image(to, image_url, caption):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/image"
    data = {"token": TOKEN, "to": to, "image": image_url, "caption": caption}
    try:
        time.sleep(1)
        r = requests.post(url, data=data, timeout=15)
        if r.status_code != 200:
            send_whatsapp(to, caption)
    except:
        send_whatsapp(to, caption)

def notify_boss(client, msg):
    try:
        alert = f"🔔 TOMMY SALE ALERT\nClient: {client}\nMsg: {msg}\nTime: {datetime.now().strftime('%H:%M')}"
        send_whatsapp(BOSS_NUMBER, alert)
    except: pass

# --- CHATGPT-STYLE BRAIN FOR BUSINESS DISCOVERY ---
def tommy_ai_brain(body, from_number):
    body_low = body.lower()
    
    # Init memory
    if from_number not in user_memory:
        user_memory[from_number] = {"stage": "new", "need": "", "budget": "", "size": ""}

    # 1. TERMS QUESTIONS - Like ChatGPT knows policy
    if any(x in body_low for x in ["terms", "conditions", "policy", "return", "warranty", "delivery", "how long", "masaa", "kurudisha"]):
        if "delivery" in body_low or "fika" in body_low:
            return "Delivery Terms, Client: Nairobi KSh 200 same day, Thika KSh 150 same day, Outside KSh 300 (24hrs). Free delivery above KSh 10k, Client. By order of Peaky Blinders, we are fast, Client. Where are you located, Client?"
        if "return" in body_low or "rudisha" in body_low:
            return "Return Policy, Client: You can exchange size within 24hrs if not worn, Client. No return after wearing. Check with rider before paying, Client. We guarantee quality, Client."
        if "payment" in body_low or "lipa" in body_low or "mpesa" in body_low:
            return f"Payment, Client: Lipa na M-Pesa {MPESA} - Legan Enterprises. Pay before delivery, send code here. We confirm instantly, Client. Secure, Client."
        return f"{TERMS_AND_CONDITIONS}\n\nAsk me anything about delivery, payment or returns, Client. I'm like ChatGPT for Legan Enterprises, Client."

    # 2. DISCOVERY - Like ChatGPT asks questions
    if any(x in body_low for x in ["nataka", "need", "looking", "nauza", "tafuta", "nini", "help", "advice", "nivae nini"]):
        if "wedding" in body_low or "harusi" in body_low or "ruracio" in body_low:
            user_memory[from_number]["need"] = "wedding"
            return "Wedding, Client? Sharp! For groom or guest, Client? What's your budget, Client? 4,500 Blazer, 7k Full Suit. What size, Client? And what color do you love, Client - Black or Navy? I will recommend best, Client."
        if "office" in body_low or "job" in body_low or "interview" in body_low or "kazi" in body_low:
            user_memory[from_number]["need"] = "office"
            return "Office/Interview, Client? Boss look needed, Client. Do you need Blazer + Trouser or Full Suit, Client? Size? Budget is 4,500-7k. I recommend Navy or Grey, Client - very official, Client."
        if "church" in body_low or "kanisa" in body_low:
            return "Church, Client? Classic look, Client. Blazer or Suit, Client? Size? We have very decent colors, Client - Black, Grey. When is church, Client? We can deliver tomorrow, Client."
        
        # General discovery
        return "I got you, Client! Like ChatGPT, I will help you discover best style, Client.\n\nTell me, Client:\n1. Occasion? (Wedding/Office/Church/Casual)\n2. Your Size? (e.g 50, or shoe 42)\n3. Budget? (e.g 4k)\n\nI will recommend exact product, Client. By order of Peaky Blinders, Client."

    # 3. PRODUCTS WITH AI RECOMMENDATION
    if any(x in body_low for x in ["blazer", "bleza", "suit", "suti", "coat", "koti"]):
        # Extract size if mentioned
        size = "".join(filter(lambda x: x.isdigit(), body_low))
        if size: user_memory[from_number]["size"] = size
        
        return f"Smart choice, Client! For your size {user_memory[from_number].get('size',''), Client}:\n\n👔 Blazer KSh 4,500 - Colors {PRODUCTS_DB['blazers']['colors']}, Sizes {PRODUCTS_DB['blazers']['sizes']}\n🤵 Full Suit KSh 7,000 - Best for Wedding/Office\n🧥 Long Coat KSh 5,500 - Cold season boss look\n\nWhich one fits your occasion, Client? Say 'Blazer photo' I send photo + Terms, Client.\n\n{PRODUCTS_DB['blazers']['for']}", True, "blazer"

    if any(x in body_low for x in ["shoe", "viatu", "kiatu", "boots", "sneaker"]):
        return f"Shoes Discovery, Client! Like ChatGPT, I recommend:\n\n👞 Formal KSh 3,500 - For Office/Wedding - Sizes 39-45\n🥾 Boots KSh 4,000 - Peaky Style - Sizes 40-45\n👟 Sneakers KSh 2,800 - Casual\n\nWhat size, Client? And for what occasion? I will pick best for you, Client.", True, "shoes"

    if any(x in body_low for x in ["bei", "price", "how much", "cost", "pesa ngapi"]):
        return f"Prices AI List, Client:\nBlazers 4.5k | Coats 5.5k | Suits 7k\nFormal Shoes 3.5k | Boots 4k | Sneakers 2.8k | Kids 2.5k\n\nDelivery 150-300. M-Pesa {MPESA}\n\nWhat is your budget, Client? I will find best within budget, like ChatGPT, Client."

    # 4. ORDER INTENT - CAPTURE LIKE CHATGPT
    if len(body) > 12 and any(x in body_low for x in ["size", "thika", "nairobi", "deliver", "nataka", "46", "50", "52", "42", "43"]):
        notify_boss(from_number, body)
        return f"Order Captured, Client! AI Discovery complete, Client.\n\nYour Order: {body}\n\nBy order of Peaky Blinders:\n✅ Stock checked - Available, Client\n✅ Terms: Pay {MPESA} before delivery\n✅ Delivery: Same day if order before 5pm\n✅ Return: Exchange within 24hrs\n\nSend M-Pesa code after paying, Client. Tommy is processing like ChatGPT speed, Client."

    # 5. GREETING - CHATGPT STYLE
    if any(x in body_low for x in ["hi", "hello", "mambo", "sasa", "niaje", "habari", "poa"]):
        return f"Hello Client! Tommy Shelby - AI for {BUSINESS_NAME}, Client. I work like ChatGPT but for menswear, Client.\n\nI can:\n1. Discover your style (ask occasion, size, budget)\n2. Show photos & prices\n3. Explain Terms, Delivery, Payment\n4. Place order 24/7\n\nWhat occasion are you dressing for, Client? Wedding, Office, Church, or Casual?"

    # FALLBACK CHATGPT STYLE
    return f"Yes Client, I'm Tommy AI, Client - Like ChatGPT for business, Client. I understand you, Client: '{body}'\n\nLet me help you discover, Client:\nReply:\n1. Menswear (Blazers/Suits)\n2. Shoes\n3. Terms & Delivery\n4. Order Now\n\nOr just tell me like 'Nataka blazer ya wedding size 50' - I understand like ChatGPT, Client."

def get_reply(body, from_number):
    result = tommy_ai_brain(body, from_number)
    
    if isinstance(result, tuple):
        text, has_image, prod_type = result
        if prod_type == "blazer":
            return {"text": text, "image": "https://i.imgur.com/8Km9tLL.jpg", "caption": text}
        if prod_type == "shoes":
            return {"text": text, "image": "https://i.imgur.com/2v4qW3p.jpg", "caption": text}
    else:
        text = result
    
    return {"text": text, "type": "text"}

@app.route("/")
def home():
    return "TOMMY V4 - CHATGPT FOR BUSINESS - LIVE - TERMS INCLUDED"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data: return "ok", 200
        msg_data = data.get('data', {})
        from_number = msg_data.get('from', '')
        body = msg_data.get('body', '')
        if not from_number or not body or msg_data.get('fromMe'): return "ok", 200
        if "@g.us" in from_number: return "ok", 200

        print(f"[{datetime.now()}] {from_number}: {body}")
        reply = get_reply(body, from_number)
        
        if "image" in reply:
            send_image(from_number, reply["image"], reply["text"][:900])
        else:
            send_whatsapp(from_number, reply["text"])
            
    except Exception as e:
        print(f"Error {e}")
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
