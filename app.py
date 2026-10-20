from flask import Flask, request
import requests

app = Flask(__name__)

INSTANCE_ID = "instance194905"
TOKEN = "4micq16wz3a5yd8b"

def send_whatsapp(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    data = {"token": TOKEN, "to": to, "body": message}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

@app.route("/")
def home():
    return "TOMMY UNIVERSAL BOT IS LIVE - Peaky Blinders"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data:
            return "ok", 200
        msg_data = data.get('data', {})
        from_number = msg_data.get('from', '')
        body = msg_data.get('body', '').lower()
        if not from_number or not body:
            return "ok", 200
        print(f"From {from_number}: {body}")
        if "hi" in body or "hello" in body or "mambo" in body:
            reply = "Hello Client! Tommy from Peaky Blinders here, Legan Enterprises.\n\nWe have:\n1. Menswear - Blazers, Coats, Suits\n2. Kids Clothes\n3. Shoes\n4. Order / Delivery\n\nWhat are you looking for, Client?"
        elif "1" in body or "blazer" in body or "coat" in body:
            reply = "Sharp choice, Client! Menswear:\n- Peaky Coats - KSh 5,500\n- Blazers - KSh 4,500\n- Suits - KSh 7,000\nSend size + location, Client."
        elif "2" in body or "kid" in body:
            reply = "Kids Suits - KSh 2,500, Kids Coats - KSh 2,000. What age, Client?"
        elif "3" in body or "shoe" in body:
            reply = "Shoes: Formal KSh 3,500, Boots KSh 4,000, Sneakers KSh 2,800. Size?"
        elif "4" in body or "order" in body:
            reply = "Ready to order, Client? Send: What you want + Size + Location. Lipa M-Pesa 0714918723"
        else:
            reply = "Yes Client, I'm here! Reply 1 Menswear, 2 Kids, 3 Shoes, 4 Order. Or tell me what you need!"
        send_whatsapp(from_number, reply)
    except Exception as e:
        print(f"Error {e}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
