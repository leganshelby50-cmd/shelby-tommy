const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const CONFIG = {
  PAY_TILL: '0714918723',
  CONTACT: '0739394981',
  NAME: 'Legan Graphics',
  ULTRAMSG_INSTANCE: 'instance194905',
  ULTRAMSG_TOKEN: '4micq16wz3a5yd8b',
  PRICES: { poster: 150, logo: 300, business_card: 200, flyer: 150, banner: 250, video: 500, thumbnail: 100, website: 5000 }
};

let clientMemory = new Map();

class TommyAI {
  detectGreeting(text) {
    const t = String(text).toLowerCase();
    if (/(sasa|niaje|mambo|poa)/.test(t)) return "Poa poa! Niko fiti, unahitaji nini leo?";
    if (t.includes('morning')) return "Good morning! Ready to design something amazing today?";
    if (t.includes('afternoon')) return "Good afternoon boss! What can I create for you?";
    if (t.includes('evening')) return "Good evening! Still working, what do you need?";
    if (/(habari|shikamoo)/.test(t)) return "Nzuri sana! Karibu, unahitaji huduma gani?";
    if (/(salaam|asalam)/.test(t)) return "Wa alaikum salaam! Karibu sana boss";
    if (/^(hi|hello|hey|hii)/.test(t.trim())) return "Hey! Legan Graphics here, what design can I do for you today?";
    return null;
  }
  understandIntent(text) {
    const t = String(text).toLowerCase();
    if (/(bei|price|how much|cost|pesa ngapi)/.test(t)) return 'PRICE';
    if (/(lipa|pay|till|mpesa)/.test(t)) return 'PAYMENT';
    if (/(work|sample|portfolio|kazi zako|onyesha)/.test(t)) return 'PORTFOLIO';
    if (/(revision|rudi)/.test(t)) return 'REVISION';
    if (/(legan|human|owner)/.test(t)) return 'HANDOVER';
    if (/(haraka|urgent|fast|30 min)/.test(t)) return 'RUSH';
    if (/(refer|rafiki|friend)/.test(t)) return 'REFERRAL';
    if (/(asante|thanks|shukrani)/.test(t)) return 'THANKS';
    return 'GENERAL';
  }
  generateReply(phone, text) {
    const safeText = String(text || '');
    let memory = clientMemory.get(phone);
    if (!memory) memory = { count: 0, returning: false };
    memory.count = memory.count + 1;
    if (memory.count > 1) memory.returning = true;
    clientMemory.set(phone, memory);
    const greet = this.detectGreeting(safeText);
    if (greet && safeText.length < 25) return greet;
    const intent = this.understandIntent(safeText);
    const t = safeText.toLowerCase();
    if ((t.includes('20 bob') || t.includes('30 bob') || t.includes('50 bob')) && !t.includes('500')) {
      return "Boss siwezi 20 bob quality ni high sana. Lowest ni Poster KES " + CONFIG.PRICES.poster + " Logo KES " + CONFIG.PRICES.logo;
    }
    if (intent === 'PRICE') {
      if (t.includes('logo')) {
        let p = memory.returning ? Math.round(CONFIG.PRICES.logo * 0.9) : CONFIG.PRICES.logo;
        let msg = "Logo design ni KES " + CONFIG.PRICES.logo + " boss. Unapata 3 concepts + source file + mockup.";
        if (memory.returning) msg = msg + " Na juu wewe ni returning client, 10% OFF = KES " + p;
        msg = msg + "\n\nLipa: " + CONFIG.PAY_TILL;
        return msg;
      }
      return "Bei zetu:\nPoster: " + CONFIG.PRICES.poster + "\nLogo: " + CONFIG.PRICES.logo + "\nBusiness Card: " + CONFIG.PRICES.business_card + "\nVideo: " + CONFIG.PRICES.video + "\nThumbnail: " + CONFIG.PRICES.thumbnail + "\nWebsite: from " + CONFIG.PRICES.website + "\n\nLipa: " + CONFIG.PAY_TILL;
    }
    if (intent === 'PAYMENT') return "Lipa hapa:\nTill: " + CONFIG.PAY_TILL + "\nName: Legan Graphics\nTuma screenshot after kulipa";
    if (intent === 'PORTFOLIO') return "Kazi zangu:\nChurch Posters\nBusiness Logos 3D\nEvent Banners\nThumbnails\nNiko na samples ready! Unataka poster ama logo?";
    if (intent === 'REVISION') return "Revision policy:\n2 FREE revisions\n3rd = KES 50 extra\nTuma changes!";
    if (intent === 'HANDOVER') return "Sawa boss, nakuhunganisha na Legan\n" + CONFIG.CONTACT;
    if (intent === 'RUSH') return "Haraka? Rush 30 mins = Price x2 = KES " + (CONFIG.PRICES.poster * 2);
    if (intent === 'REFERRAL') return "Referral: Leta rafiki, unapata KES 50 OFF!";
    if (intent === 'THANKS') return "Shukrani boss! File ready HD. Unahitaji business card pia? KES 150 tu. " + CONFIG.CONTACT;
    let hour = new Date().getHours();
    let off = (hour >= 22 || hour < 6) ? "\n\nNiko offline usiku but order nimei-save!" : "";
    return "Sawa boss! Nimekuelewa\nEleza design unataka (rangi, jina, style) niundie kitu kali.\nBei from KES " + CONFIG.PRICES.poster + "\nLipa: " + CONFIG.PAY_TILL + off + "\n\nNiko tayari!";
  }
}

const tommy = new TommyAI();

async function sendWhatsAppMessage(to, message) {
  try {
    const url = "https://api.ultramsg.com/" + CONFIG.ULTRAMSG_INSTANCE + "/messages/chat";
    await axios.post(url, { token: CONFIG.ULTRAMSG_TOKEN, to: to, body: message });
    return true;
  } catch (e) {
    console.log("ULTRAMSG Error: " + e.message);
    return false;
  }
}

app.post('/ultramsg-webhook', async (req, res) => {
  try {
    const body = req.body;
    const data = body.data || body;
    if (!data) return res.sendStatus(200);
    if (data.fromMe === true) return res.sendStatus(200);
    const phone = data.from || data.chatId || "";
    const message = data.body || data.text || "";
    if (!phone || !message) return res.sendStatus(200);
    const reply = tommy.generateReply(phone, message);
    await sendWhatsAppMessage(phone, reply);
    res.sendStatus(200);
  } catch (e) {
    res.sendStatus(200);
  }
});

app.get('/dashboard', (req, res) => {
  res.json({
    business: CONFIG.NAME,
    contact: CONFIG.CONTACT,
    pay: CONFIG.PAY_TILL,
    clients: clientMemory.size,
    method: 'GITHUB + RENDER + ULTRAMSG NO CHALLENGE',
    status: 'PURE AI ONLINE 38 POWERS ERROR FREE',
    bot: false,
    ai: true
  });
});

app.get('/', (req, res) => {
  res.send('<h1>TOMMY PURE AI ONLINE NO CHALLENGE</h1><p>Legan ' + CONFIG.CONTACT + ' Pay ' + CONFIG.PAY_TILL + '</p><p>Render + UltraMsg</p><p><a href="/dashboard">Dashboard</a></p>');
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log("TOMMY PURE AI ONLINE PORT " + PORT + " NO CHALLENGE ERROR FREE");
});

module.exports = app;
