from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

CONFIG = {
    "PAY_TILL": "0714918723",
    "CONTACT": "0739394981",
    "NAME": "Legan Graphics",
    "ULTRAMSG_INSTANCE": "instance194905",
    "ULTRAMSG_TOKEN": "4micq16wz3a5yd8b",
    "PRICES": {
        "poster": 150, "logo": 300, "business_card": 200,
        "flyer": 150, "banner": 250, "video": 500,
        "thumbnail": 100, "website": 5000,
        "social_pack": 800, "brand_kit": 1500
    }
}

client_memory = {}
orders = []

class TommyPureAI:
    def __init__(self):
        self.powers = 38

    def detect_greeting(self, text):
        t = str(text).lower()
        if any(x in t for x in ["sasa","niaje","mambo","poa"]):
            return "Poa poa! Niko fiti, unahitaji nini leo?"
        if "morning" in t:
            return "Good morning boss! Ready to design something amazing today?"
        if "afternoon" in t:
            return "Good afternoon! What can I create for you?"
        if "evening" in t:
            return "Good evening! Still working, what do you need?"
        if any(x in t for x in ["habari","shikamoo"]):
            return "Nzuri sana! Karibu, unahitaji huduma gani?"
        if any(x in t for x in ["salaam","asalam"]):
            return "Wa alaikum salaam! Karibu sana boss"
        if t.strip().startswith(("hi","hello","hey","hii")):
            return "Hey! Legan Graphics here, what design can I do for you today?"
        return None

    def understand_intent(self, text):
        t = str(text).lower()
        if any(x in t for x in ["bei","price","how much","cost","pesa ngapi","garama"]):
            return "PRICE"
        if any(x in t for x in ["lipa","pay","till","mpesa","paybill"]):
            return "PAYMENT"
        if any(x in t for x in ["work","sample","portfolio","kazi zako","onyesha","designs"]):
            return "PORTFOLIO"
        if any(x in t for x in ["revision","rudi","badilisha","change"]):
            return "REVISION"
        if any(x in t for x in ["legan","human","owner","ongea na","call"]):
            return "HANDOVER"
        if any(x in t for x in ["haraka","urgent","fast","30 min","emergency"]):
            return "RUSH"
        if any(x in t for x in ["refer","rafiki","friend","jamaa"]):
            return "REFERRAL"
        if any(x in t for x in ["asante","thanks","shukrani","thank you"]):
            return "THANKS"
        if "poster" in t or "bango" in t:
            return "POSTER"
        if "logo" in t:
            return "LOGO"
        if "business card" in t or "card" in t:
            return "CARD"
        if "flyer" in t:
            return "FLYER"
        if "banner" in t:
            return "BANNER"
        if "video" in t or "edit" in t:
            return "VIDEO"
        if "thumbnail" in t:
            return "THUMBNAIL"
        if "website" in t or "web" in t:
            return "WEBSITE"
        if "social" in t or "pack" in t:
            return "SOCIAL_PACK"
        if "brand" in t or "kit" in t:
            return "BRAND_KIT"
        return "GENERAL"

    def generate_reply(self, phone, text):
        safe_text = str(text or "")
        memory = client_memory.get(phone)
        if not memory:
            memory = {"count":0,"returning":False,"orders":0}
        memory["count"] += 1
        if memory["count"] > 1:
            memory["returning"] = True
        client_memory[phone] = memory

        greet = self.detect_greeting(safe_text)
        if greet and len(safe_text) < 25:
            return greet

        t = safe_text.lower()
        intent = self.understand_intent(safe_text)

        if any(x in t for x in ["20 bob","30 bob","50 bob","100 bob"]) and "500" not in t and "800" not in t:
            return f"Boss siwezi 20-100 bob, quality ni high sana. Lowest ni Poster KES {CONFIG['PRICES']['poster']}, Logo KES {CONFIG['PRICES']['logo']}. Hiyo ndio best price."

        discount_text = "\nNa juu wewe ni returning client, 10% OFF!" if memory["returning"] else ""

        if intent == "PRICE":
            return f"""Bei zetu boss:
Poster: {CONFIG['PRICES']['poster']}
Logo: {CONFIG['PRICES']['logo']} (3 concepts + mockup + source)
Business Card: {CONFIG['PRICES']['business_card']}
Flyer: {CONFIG['PRICES']['flyer']}
Banner: {CONFIG['PRICES']['banner']}
Video: {CONFIG['PRICES']['video']}
Thumbnail: {CONFIG['PRICES']['thumbnail']}
Social Pack (10 posts): {CONFIG['PRICES']['social_pack']}
Brand Kit: {CONFIG['PRICES']['brand_kit']}
Website: from {CONFIG['PRICES']['website']}{discount_text}

Lipa: {CONFIG['PAY_TILL']}"""

        if intent == "POSTER":
            return f"Poster ni KES {CONFIG['PRICES']['poster']} boss. Unapata HD + print ready. Nipe jina, rangi, na details niundie kitu kali. Lipa: {CONFIG['PAY_TILL']}{discount_text}"
        if intent == "LOGO":
            p = int(CONFIG['PRICES']['logo']*0.9) if memory['returning'] else CONFIG['PRICES']['logo']
            return f"Logo design ni KES {CONFIG['PRICES']['logo']} (returning KES {p}). Unapata 3 concepts + source file + 3D mockup + revisions 2 free. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "CARD":
            return f"Business Card ni KES {CONFIG['PRICES']['business_card']} both sides design + print ready PDF. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "FLYER":
            return f"Flyer ni KES {CONFIG['PRICES']['flyer']} A5 HD ready for print. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "BANNER":
            return f"Banner ni KES {CONFIG['PRICES']['banner']} big size HD. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "VIDEO":
            return f"Video editing ni KES {CONFIG['PRICES']['video']} per minute - cuts, transitions, text, music. Tuma raw files. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "THUMBNAIL":
            return f"YouTube Thumbnail ni KES {CONFIG['PRICES']['thumbnail']} clickbait design high CTR. Lipa: {CONFIG['PAY_TILL']}"
        if intent == "WEBSITE":
            return f"Website from KES {CONFIG['PRICES']['website']} boss - responsive, fast, na SEO. Domain + hosting separate. Lipa: {CONFIG['PAY_TILL']}\nCall: {CONFIG['CONTACT']}"
        if intent == "SOCIAL_PACK":
            return f"Social Media Pack ni KES {CONFIG['PRICES']['social_pack']} - 10 posts branded. Best deal! Lipa: {CONFIG['PAY_TILL']}{discount_text}"
        if intent == "BRAND_KIT":
            return f"Brand Kit ni KES {CONFIG['PRICES']['brand_kit']} - Logo + Business Card + Letterhead + Social kit. Full branding! Lipa: {CONFIG['PAY_TILL']}"
        if intent == "PAYMENT":
            return f"Lipa hapa:\nTill: {CONFIG['PAY_TILL']}\nName: Legan Graphics\n\nAfter kulipa tuma screenshot na jina ya design unataka. Naanza mara moja!"
        if intent == "PORTFOLIO":
            return "Kazi zangu:\nChurch Posters - kali sana\nBusiness Logos 3D\nEvent Banners\nYouTube Thumbnails\nBusiness Cards\nTuko na 500+ designs done! Unataka niundie gani leo?"
        if intent == "REVISION":
            return "Revision policy:\n2 FREE revisions within 24hrs\n3rd revision = KES 50 extra\nTuma changes clearly ni-fix haraka!"
        if intent == "HANDOVER":
            return f"Sawa boss, nakuhunganisha na Legan mwenyewe\n{CONFIG['CONTACT']}\nAtakujibu ASAP!"
        if intent == "RUSH":
            return f"Haraka? Rush order 30 mins = Price x2\nPoster rush = KES {CONFIG['PRICES']['poster']*2}\nLogo rush = KES {CONFIG['PRICES']['logo']*2}\nConfirm nikuanzie?"
        if intent == "REFERRAL":
            return "Referral bonus: Leta rafiki akilipa, wewe unapata KES 50 OFF next order! Na yeye pia 10% OFF. Win-win!"
        if intent == "THANKS":
            return f"Shukrani sana boss! Karibu tena. File ready HD. Unahitaji business card pia? KES 150 tu. {CONFIG['CONTACT']}"

        hour = datetime.now().hour
        time_note = "\nNiko offline usiku but order nimei-save, naanza asubuhi 6am!" if hour >=22 or hour <6 else ""
        upsell = f"\n\nTip: Watu wengi wanachukua Poster + Logo combo KES {CONFIG['PRICES']['poster']+CONFIG['PRICES']['logo']-50} (save 50)!" if memory["orders"]==0 else ""
        return f"Sawa boss! Nimekuelewa\nEleza design unataka:\n- Jina/Text\n- Rangi\n- Style (modern, church, business)\nNiundie kitu kali.\nBei from KES {CONFIG['PRICES']['poster']}\nLipa: {CONFIG['PAY_TILL']}{time_note}{upsell}\n\nNiko tayari!"

tommy = TommyPureAI()

def send_whatsapp_message(to, message):
    try:
        url = f"https://api.ultramsg.com/{CONFIG['ULTRAMSG_INSTANCE']}/messages/chat"
        requests.post(url, json={"token":CONFIG['ULTRAMSG_TOKEN'],"to":to,"body":message})
        return True
    except Exception as e:
        print(f"ULTRAMSG Error: {e}")
        return False

@app.route('/ultramsg-webhook', methods=['POST'])
def ultramsg_webhook():
    try:
        body = request.json or {}
        data = body.get('data', body)
        if not data:
            return '', 200
        if data.get('fromMe') == True:
            return '', 200
        phone = data.get('from') or data.get('chatId') or ""
        message = data.get('body') or data.get('text') or ""
        if not phone or not message:
            return '', 200
        orders.append({"phone":phone,"message":message,"time":str(datetime.now())})
        reply = tommy.generate_reply(phone, message)
        send_whatsapp_message(phone, reply)
        return '', 200
    except:
        return '', 200

@app.route('/dashboard')
def dashboard():
    return jsonify({
        "business": CONFIG["NAME"],
        "contact": CONFIG["CONTACT"],
        "pay": CONFIG["PAY_TILL"],
        "clients": len(client_memory),
        "total_messages": len(orders),
        "method": "GITHUB + RENDER + ULTRAMSG PYTHON NO CHALLENGE FULL 38 POWERS",
        "status": "PURE AI ONLINE 38 POWERS ERROR FREE",
        "powers": tommy.powers,
        "bot": False,
        "ai": True
    })

@app.route('/')
def home():
    return f"<h1>TOMMY PURE AI FULL 38 POWERS PYTHON ONLINE</h1><p>Legan {CONFIG['CONTACT']} Pay {CONFIG['PAY_TILL']}</p><p>Python 3 - No Challenge - Error Free</p><p><a href='/dashboard'>Dashboard</a></p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
