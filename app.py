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
  PRICES: { poster: 150, logo: 300, business_card: 200, flyer: 150, banner: 250, video: 500, thumbnail: 100, website: 5000, social_pack: 800, brand_kit: 1500 }
};

let clientMemory = new Map();
let orders = [];

class TommyPureAI {
  constructor() {
    this.powers = 38;
  }

  // POWER 1-7 GREETINGS
  detectGreeting(text) {
    const t = String(text).toLowerCase();
    if (/(sasa|niaje|mambo|poa)/.test(t)) return "Poa poa! Niko fiti, unahitaji nini leo?";
    if (t.includes('morning')) return "Good morning boss! Ready to design something amazing today?";
    if (t.includes('afternoon')) return "Good afternoon! What can I create for you?";
    if (t.includes('evening')) return "Good evening! Still working, what do you need?";
    if (/(habari|shikamoo)/.test(t)) return "Nzuri sana! Karibu, unahitaji huduma gani?";
    if (/(salaam|asalam)/.test(t)) return "Wa alaikum salaam! Karibu sana boss";
    if (/^(hi|hello|hey|hii)/.test(t.trim())) return "Hey! Legan Graphics here, what design can I do for you today?";
    return null;
  }

  // POWER 8-20 INTENT
  understandIntent(text) {
    const t = String(text).toLowerCase();
    if (/(bei|price|how much|cost|pesa ngapi|garama)/.test(t)) return 'PRICE';
    if (/(lipa|pay|till|mpesa|paybill)/.test(t)) return 'PAYMENT';
    if (/(work|sample|portfolio|kazi zako|onyesha|designs)/.test(t)) return 'PORTFOLIO';
    if (/(revision|rudi|badilisha|change)/.test(t)) return 'REVISION';
    if (/(legan|human|owner|ongea na|call)/.test(t)) return 'HANDOVER';
    if (/(haraka|urgent|fast|30 min|emergency)/.test(t)) return 'RUSH';
    if (/(refer|rafiki|friend|jamaa)/.test(t)) return 'REFERRAL';
    if (/(asante|thanks|shukrani|thank you)/.test(t)) return 'THANKS';
    if (/(poster|bango)/.test(t)) return 'POSTER';
    if (/(logo)/.test(t)) return 'LOGO';
    if (/(business card|card)/.test(t)) return 'CARD';
    if (/(flyer)/.test(t)) return 'FLYER';
    if (/(banner)/.test(t)) return 'BANNER';
    if (/(video|edit)/.test(t)) return 'VIDEO';
    if (/(thumbnail)/.test(t)) return 'THUMBNAIL';
    if (/(website|web)/.test(t)) return 'WEBSITE';
    if (/(social|pack)/.test(t)) return 'SOCIAL_PACK';
    if (/(brand|kit)/.test(t)) return 'BRAND_KIT';
    return 'GENERAL';
  }

  // POWER 21-38 FULL AI LOGIC
  generateReply(phone, text) {
    const safeText = String(text || '');
    let memory = clientMemory.get(phone);
    if (!memory) memory = { count: 0, returning: false, name: '', orders: 0, lastOrder: '' };
    memory.count = memory.count + 1;
    if (memory.count > 1) memory.returning = true;
    memory.lastSeen = new Date();
    clientMemory.set(phone, memory);

    const greet = this.detectGreeting(safeText);
    if (greet && safeText.length < 25) return greet;

    const t = safeText.toLowerCase();
    const intent = this.understandIntent(safeText);

    // Power: Anti lowball
    if ((t.includes('20 bob') || t.includes('30 bob') || t.includes('50 bob') || t.includes('100 bob')) && !t.includes('500') && !t.includes('800') && !t.includes('1500')) {
      return "Boss siwezi 20-100 bob, quality ni high sana. Lowest ni Poster KES " + CONFIG.PRICES.poster + ", Logo KES " + CONFIG.PRICES.logo + ". Hiyo ndio best price.";
    }

    // Power: Returning client discount
    let discountText = "";
    if (memory.returning) discountText = "\nNa juu wewe ni returning client, 10% OFF!";

    if (intent === 'PRICE') {
      return "Bei zetu boss:\nPoster: " + CONFIG.PRICES.poster + "\nLogo: " + CONFIG.PRICES.logo + " (3 concepts + mockup + source)\nBusiness Card: " + CONFIG.PRICES.business_card + "\nFlyer: " + CONFIG.PRICES.flyer + "\nBanner: " + CONFIG.PRICES.banner + "\nVideo: " + CONFIG.PRICES.video + "\nThumbnail: " + CONFIG.PRICES.thumbnail + "\nSocial Media Pack (10 posts): " + CONFIG.PRICES.social_pack + "\nBrand Kit: " + CONFIG.PRICES.brand_kit + "\nWebsite: from " + CONFIG.PRICES.website + discountText + "\n\nLipa: " + CONFIG.PAY_TILL;
    }
    if (intent === 'POSTER') return "Poster ni KES " + CONFIG.PRICES.poster + " boss. Unapata HD + print ready. Nipe jina, rangi, na details niundie kitu kali. Lipa: " + CONFIG.PAY_TILL + discountText;
    if (intent === 'LOGO') {
      let p = memory.returning ? Math.round(CONFIG.PRICES.logo * 0.9) : CONFIG.PRICES.logo;
      return "Logo design ni KES " + CONFIG.PRICES.logo + " (returning KES " + p + "). Unapata 3 concepts + source file + 3D mockup + revisions 2 free. Lipa: " + CONFIG.PAY_TILL;
    }
    if (intent === 'CARD') return "Business Card ni KES " + CONFIG.PRICES.business_card + " both sides design + print ready PDF. Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'FLYER') return "Flyer ni KES " + CONFIG.PRICES.flyer + " A5 HD ready for print. Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'BANNER') return "Banner ni KES " + CONFIG.PRICES.banner + " big size HD. Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'VIDEO') return "Video editing ni KES " + CONFIG.PRICES.video + " per minute - cuts, transitions, text, music. Tuma raw files. Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'THUMBNAIL') return "YouTube Thumbnail ni KES " + CONFIG.PRICES.thumbnail + " clickbait design high CTR. Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'WEBSITE') return "Website from KES " + CONFIG.PRICES.website + " boss - responsive, fast, na SEO. Domain + hosting separate. Lipa: " + CONFIG.PAY_TILL + "\nCall: " + CONFIG.CONTACT;
    if (intent === 'SOCIAL_PACK') return "Social Media Pack ni KES " + CONFIG.PRICES.social_pack + " - 10 posts branded for your business. Best deal! Lipa: " + CONFIG.PAY_TILL + discountText;
    if (intent === 'BRAND_KIT') return "Brand Kit ni KES " + CONFIG.PRICES.brand_kit + " - Logo + Business Card + Letterhead + Social kit. Full branding! Lipa: " + CONFIG.PAY_TILL;
    if (intent === 'PAYMENT') return "Lipa hapa:\nTill: " + CONFIG.PAY_TILL + "\nName: Legan Graphics\n\nAfter kulipa tuma screenshot na jina ya design unataka. Naanza mara moja!";
    if (intent === 'PORTFOLIO') return "Kazi zangu:\nChurch Posters - kali sana\nBusiness Logos 3D\nEvent Banners\nYouTube Thumbnails\nBusiness Cards\nTuko na 500+ designs done! Unataka niundie gani leo?";
    if (intent === 'REVISION') return "Revision policy:\n2 FREE revisions within 24hrs\n3rd revision = KES 50 extra\nTuma changes clearly ni-fix haraka!";
    if (intent === 'HANDOVER') return "Sawa boss, nakuhunganisha na Legan mwenyewe\n" + CONFIG.CONTACT + "\nAtakujibu ASAP!";
    if (intent === 'RUSH') return "Haraka? Rush order 30 mins = Price x2\nPoster rush = KES " + (CONFIG.PRICES.poster * 2) + "\nLogo rush = KES " + (CONFIG.PRICES.logo * 2) + "\nConfirm nikuanzie?";
    if (intent === 'REFERRAL') return "Referral bonus: Leta rafiki akilipa, wewe unapata KES 50 OFF next order! Na yeye pia 10% OFF. Win-win!";
    if (intent === 'THANKS') return "Shukrani sana boss! Karibu tena. File ready HD. Unahitaji business card pia? KES 150 tu. " + CONFIG.CONTACT;

    // Power: Time awareness
    let hour = new Date().getHours();
    let timeNote = "";
    if (hour >= 22 || hour < 6) timeNote = "\nNiko offline usiku but order nimei-save, naanza asubuhi 6am!";
    else if (hour >= 6 && hour < 12) timeNote = "\nAsubuhi njema! Niko active sai.";
    
    // Power: Upsell
    let upsell = "";
    if (memory.orders === 0) upsell = "\n\nTip: Watu wengi wanachukua Poster + Logo combo KES " + (CONFIG.PRICES.poster + CONFIG.PRICES.logo - 50) + " (save 50)!";

    return "Sawa boss! Nimekuelewa\nEleza design unataka:\n- Jina/Text\n- Rangi\n- Style (modern, church, business)\nNiundie kitu kali.\nBei from KES " + CONFIG.PRICES.poster + "\nLipa: " + CONFIG.PAY_TILL + timeNote + upsell + "\n\nNiko tayari!";
  }
}

const tommy = new TommyPureAI();

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
    orders.push({ phone, message, time: new Date() });
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
    total_messages: orders.length,
    method: 'GITHUB + RENDER + ULTRAMSG NO CHALLENGE FULL 38 POWERS',
    status: 'PURE AI ONLINE 38 POWERS ERROR FREE',
    powers: tommy.powers,
    bot: false,
    ai: true,
    version: 'FULL TOMMY PURE AI'
  });
});

app.get('/', (req, res) => {
  res.send('<h1>TOMMY PURE AI FULL 38 POWERS ONLINE</h1><p>Legan ' + CONFIG.CONTACT + ' Pay ' + CONFIG.PAY_TILL + '</p><p>Full 38 Powers - Render + UltraMsg - No Challenge - Error Free</p><p><a href="/dashboard">Dashboard</a></p>');
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log("TOMMY PURE AI FULL 38 POWERS ONLINE PORT " + PORT + " NO CHALLENGE ERROR FREE");
});

module.exports = app;
