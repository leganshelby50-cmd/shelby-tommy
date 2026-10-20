from flask import Flask, request
import requests

app = Flask(__name__)

# YOUR ULTRAMSG DETAILS
INSTANCE_ID = "instance194905"
TOKEN = "  #4micq16wz3a5yd8b" <--- PASTE YOUR TOKEN HERE
def send_whatsapp(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    data = {
        "token": TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, data=data)

@app.route("/")
def home():
    return "TOMMY UNIVERSAL BOT IS LIVE - Peaky Blinders"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return "ok", 200
    
    # Get message
    try:
        msg_data = data.get('data', {})
        from_number = msg_data.get('from', '')
        message = msg_data.get('body', '').lower()
        
        if not from_number or not message:
            return "ok", 200

        print(f"Message from {from_number}: {message}")

        # TOMMY REPLIES - HUMAN STYLE
        if "hi" in message or "hello" in message or "mambo" in message:
            reply = """Hello Client! 🧥 Tommy from Peaky Blinders here, Legan Enterprises.

We have today:
1️⃣ Menswear - Blazers, Coats, Suits
2️⃣ Kids Clothes
3️⃣ Shoes
4️⃣ Order / Delivery

What are you looking for, Client?"""
        
        elif "1" in message or "blazer" in message or "coat" in message or "suit" in message:
            reply = """Sharp choice, Client! 🔥 Menswear:

- Peaky Blinders Coats - KSh 5,500
- Official Blazers - KSh 4,500
- Suits - KSh 7,000
- Shirts - KSh 1,800

Send your size and location, Client. We deliver today in Thika/Nairobi."""
        
        elif "2" in message or "kid" in message:
            reply = """For the little Shelby! 👶 Kids:

- Kids Suits - KSh 2,500
- Kids Coats - KSh 2,000

What age, Client?"""
        
        elif "shoe" in message or "3" in message:
            reply = """Shoes? 🔥

- Formal Shoes - KSh 3,500
- Boots - KSh 4,000
- Sneakers - KSh 2,800

What size, Client?"""
        
        elif "order" in message or "delivery" in message or "4" in message:
            reply = """Ready to order, Client? 💼

Just send:
1. What you want + Size
2. Your location
3. Your other number

We deliver in 2hrs in Thika, tomorrow Nairobi.

Lipa na M-Pesa: 0714918723"""
        
        else:
            reply = """Yes Client, I'm here! Tommy from Peaky Blinders.

Reply with:
1 - Menswear
2 - Kids
3 - Shoes
4 - Order

Or just tell me what you need, Client!"""

        send_whatsapp(from_number, reply)
        
    except Exception as e:
        print(f"Error: {e}")
    
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
