import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID", "instance194905")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN", "")
ULTRAMSG_BASE = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

@app.route("/")
def home():
    return "TOMMY UNIVERSAL BOT IS LIVE - Peaky Blinders"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "Webhook OK - Send POST from UltraMsg"
    
    try:
        data = request.json
        print("Incoming:", data)
        
        # Get message details
        msg_data = data.get('data', {})
        from_number = msg_data.get('from', '')
        message_body = msg_data.get('body', '')
        is_from_me = msg_data.get('fromMe', False)
        
        # Ignore my own messages
        if is_from_me:
            return jsonify({"status": "ignored self"}), 200
        
        if not message_body or not from_number:
            return jsonify({"status": "no message"}), 200
            
        # TOMMY REPLY
        reply_text = f"""Hello Client! 🔥
Tommy UNIVERSAL here from Peaky Blinders!

You said: {message_body}

👑 KING $HELBY SERVICES:
1. Forex Signals
2. Betting Tips
3. Business Setup
4. 24/7 Support

How can I help you today?"""

        # Send reply via UltraMsg API
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": from_number,
            "body": reply_text
        }
        
        res = requests.post(ULTRAMSG_BASE, data=payload)
        print("Reply sent:", res.text)
        
        return jsonify({"status": "replied"}), 200
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
