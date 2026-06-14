from flask import Flask, request, jsonify, render_template_string, Response
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7255636020:AAE2uVHWtRWmGl2eXjILnGCCG4hYjKsmOIg")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1003211477952")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

def send_telegram(message, photo=None):
    try:
        if photo:
            data = {"chat_id": CHANNEL_ID, "caption": message, "parse_mode": "HTML"}
            files = {"photo": photo}
            r = requests.post(TELEGRAM_PHOTO_URL, data=data, files=files)
        else:
            data = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "HTML"}
            r = requests.post(TELEGRAM_URL, json=data)
        return r.status_code == 200
    except Exception as e:
        print(f"خطا: {e}")
        return False

def build_analysis_message(data):
    symbol = data.get("symbol", "")
    trend = data.get("trend", "")
    buy_zone = data.get("buy_zone", "")
    cancel = data.get("cancel", "")
    targets = data.get("targets", [])
    description = data.get("description", "")

    msg = "━━━━━━━━━━━━━━\n"
    msg += "📊 <b>تحلیل بازار</b>\n\n"
    msg += f"📌 <b>نماد:</b> {symbol}\n"
    msg += f"📈 <b>روند:</b> {trend}\n"
    if buy_zone:
        msg += f"🎯 <b>محدوده ورود:</b>\n{buy_zone}\n"
    if cancel:
        msg += f"🛑 <b>ابطال تحلیل:</b>\n{cancel}\n"
    if targets:
        msg += "\n📍 <b>اهداف:</b>\n"
        for t in targets:
            msg += f"✅ {t}\n"
    if description:
        msg += f"\n📝 <b>توضیح:</b>\n{description}\n"
    msg += "\n⚠️ این تحلیل آموزشی است.\n"
    msg += "━━━━━━━━━━━━━━"
    return msg

def build_setup_message(data):
    symbol = data.get("symbol", "")
    direction = data.get("direction", "")
    entry = data.get("entry", "")
    sl = data.get("sl", "")
    tp1 = data.get("tp1", "")
    tp2 = data.get("tp2", "")
    tp3 = data.get("tp3", "")
    rr = data.get("rr", "")

    dir_upper = direction.upper()
    if "BUY LIMIT" in dir_upper:
        emoji = "🟡"
    elif "SELL LIMIT" in dir_upper:
        emoji = "🟠"
    elif "BUY STOP" in dir_upper:
        emoji = "🔵"
    elif "SELL STOP" in dir_upper:
        emoji = "🟣"
    elif "BUY" in dir_upper:
        emoji = "🟢"
    elif "SELL" in dir_upper:
        emoji = "🔴"
    else:
        emoji = "⚪"
    dir_fa = direction

    msg = "━━━━━━━━━━━━━━\n"
    msg += f"📢 <b>ستاپ معاملاتی</b> {emoji}\n\n"
    msg += f"📌 <b>نماد:</b> {symbol}\n"
    msg += f"📊 <b>نوع:</b> {dir_fa}\n"
    if entry:
        msg += f"🎯 <b>ناحیه ورود:</b>\n{entry}\n"
    if sl:
        msg += f"🛑 <b>استاپ:</b>\n{sl}\n"
    if tp1:
        msg += f"\n✅ <b>هدف اول:</b> {tp1}\n"
    if tp2:
        msg += f"✅ <b>هدف دوم:</b> {tp2}\n"
    if tp3:
        msg += f"✅ <b>هدف سوم:</b> {tp3}\n"
    if rr:
        msg += f"\n⚖️ <b>RR:</b> {rr}\n"
    msg += "\n⚠️ این یک ستاپ آموزشی است.\n"
    msg += "مسئولیت ورود با معامله‌گر است.\n"
    msg += "━━━━━━━━━━━━━━"
    return msg

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data:
            data = json.loads(request.data)
        msg_type = data.get("type", "setup")
        if msg_type == "analysis":
            message = build_analysis_message(data)
        else:
            message = build_setup_message(data)
        success = send_telegram(message)
        return jsonify({"status": "ok" if success else "error"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/manifest.json")
def manifest():
    data = {
        "name": "Kamalhaqjo Signal",
        "short_name": "KSignal",
        "description": "پنل سیگنال VIP کمال حق‌جو",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a0a",
        "theme_color": "#FFD700",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/icon.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }
    return jsonify(data)

@app.route("/sw.js")
def sw():
    sw_content = """
const CACHE_NAME = 'kamalhaqjo-v1';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(['/'])));
});
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
"""
    return Response(sw_content, mimetype='application/javascript')

PANEL_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="KSignal">
<meta name="theme-color" content="#FFD700">
<link rel="manifest" href="/manifest.json">
<title>🦅 Kamalhaqjo Signal</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  body { 
    background: #0a0a0a; 
    color: #f0f0f0; 
    font-family: Tahoma, sans-serif; 
    padding: 16px;
    min-height: 100vh;
    padding-bottom: 30px;
  }
  .container { max-width: 500px; margin: 0 auto; }
  h1 { 
    color: #FFD700; 
    text-align: center; 
    margin-bottom: 20px; 
    font-size: 20px;
    padding-top: 10px;
  }
  .install-btn {
    display: none;
    width: 100%;
    padding: 10px;
    background: #1a1a1a;
    border: 1px solid #FFD700;
    border-radius: 8px;
    color: #FFD700;
    font-size: 13px;
    cursor: pointer;
    margin-bottom: 15px;
    text-align: center;
  }
  .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
  .tab { 
    flex: 1; 
    padding: 12px 8px; 
    background: #1a1a1a; 
    border: 1px solid #333; 
    border-radius: 10px; 
    cursor: pointer; 
    text-align: center; 
    color: #aaa; 
    font-size: 13px;
    transition: all 0.2s;
  }
  .tab.active { background: #FFD700; color: #000; font-weight: bold; border-color: #FFD700; }
  .form-group { margin-bottom: 12px; }
  label { display: block; margin-bottom: 5px; color: #FFD700; font-size: 13px; font-weight: bold; }
  input, textarea, select { 
    width: 100%; 
    padding: 12px; 
    background: #1a1a1a; 
    border: 1px solid #2a2a2a;
    border-radius: 10px; 
    color: #f0f0f0; 
    font-size: 15px; 
    font-family: Tahoma;
    -webkit-appearance: none;
  }
  input:focus, textarea:focus, select:focus {
    border-color: #FFD700;
    outline: none;
  }
  textarea { height: 75px; resize: none; }
  select { background-image: none; }
  .btn { 
    width: 100%; 
    padding: 16px; 
    background: #FFD700; 
    color: #000; 
    border: none;
    border-radius: 12px; 
    font-size: 17px; 
    font-weight: bold; 
    cursor: pointer; 
    margin-top: 8px;
    letter-spacing: 1px;
  }
  .btn:active { background: #FFC000; transform: scale(0.98); }
  .row { display: flex; gap: 8px; }
  .row .form-group { flex: 1; }
  .status { 
    text-align: center; 
    margin-top: 12px; 
    padding: 12px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: bold;
  }
  .status.success { background: #0a2a0a; color: #00ff88; border: 1px solid #00ff88; }
  .status.error { background: #2a0a0a; color: #ff4444; border: 1px solid #ff4444; }
  .status.loading { background: #1a1a00; color: #FFD700; border: 1px solid #FFD700; }
  .divider { 
    border: none; 
    border-top: 1px solid #222; 
    margin: 15px 0; 
  }
</style>
</head>
<body>
<div class="container">
  <h1>🦅 پنل سیگنال Kamalhaqjo</h1>
  
  <button class="install-btn" id="installBtn" onclick="installApp()">
    📲 نصب اپ روی گوشی
  </button>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('setup')">📢 ستاپ معاملاتی</div>
    <div class="tab" onclick="switchTab('analysis')">📊 تحلیل بازار</div>
  </div>

  <!-- ستاپ معاملاتی -->
  <div id="setup-form">
    <div class="row">
      <div class="form-group">
        <label>نماد</label>
        <select id="s-symbol">
          <option>XAUUSD</option>
          <option>US30</option>
          <option>EURUSD</option>
          <option>GBPUSD</option>
          <option>BTCUSD</option>
        </select>
      </div>
      <div class="form-group">
        <label>نوع</label>
        <select id="s-direction">
          <option value="BUY">BUY 🟢</option>
          <option value="SELL">SELL 🔴</option>
          <option value="BUY LIMIT">BUY LIMIT 🟡</option>
          <option value="SELL LIMIT">SELL LIMIT 🟠</option>
          <option value="BUY STOP">BUY STOP 🔵</option>
          <option value="SELL STOP">SELL STOP 🟣</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>ناحیه ورود</label>
      <input type="text" id="s-entry" placeholder="مثلاً: 3340 - 3345">
    </div>
    <div class="form-group">
      <label>استاپ لاس</label>
      <input type="text" id="s-sl" placeholder="مثلاً: 3320">
    </div>
    <div class="row">
      <div class="form-group">
        <label>هدف اول</label>
        <input type="text" id="s-tp1" placeholder="TP1">
      </div>
      <div class="form-group">
        <label>هدف دوم</label>
        <input type="text" id="s-tp2" placeholder="TP2">
      </div>
      <div class="form-group">
        <label>هدف سوم</label>
        <input type="text" id="s-tp3" placeholder="TP3">
      </div>
    </div>
    <div class="form-group">
      <label>نسبت RR</label>
      <input type="text" id="s-rr" placeholder="مثلاً: 1:2">
    </div>
    <button class="btn" onclick="sendSetup()">📤 ارسال به کانال</button>
  </div>

  <!-- تحلیل بازار -->
  <div id="analysis-form" style="display:none">
    <div class="form-group">
      <label>نماد</label>
      <select id="a-symbol">
        <option>XAUUSD</option>
        <option>US30</option>
        <option>EURUSD</option>
        <option>GBPUSD</option>
        <option>BTCUSD</option>
      </select>
    </div>
    <div class="form-group">
      <label>روند</label>
      <select id="a-trend">
        <option>صعودی 📈</option>
        <option>نزولی 📉</option>
        <option>خنثی ↔️</option>
      </select>
    </div>
    <div class="form-group">
      <label>محدوده ورود</label>
      <input type="text" id="a-zone" placeholder="مثلاً: 3340 - 3345">
    </div>
    <div class="form-group">
      <label>ابطال تحلیل</label>
      <input type="text" id="a-cancel" placeholder="مثلاً: 3320">
    </div>
    <div class="form-group">
      <label>اهداف (هر هدف یک خط)</label>
      <textarea id="a-targets" placeholder="3360&#10;3375&#10;3390"></textarea>
    </div>
    <div class="form-group">
      <label>توضیح</label>
      <textarea id="a-desc" placeholder="توضیح تحلیل..."></textarea>
    </div>
    <button class="btn" onclick="sendAnalysis()">📤 ارسال به کانال</button>
  </div>

  <div id="status"></div>
</div>

<script>
// PWA Install
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  document.getElementById('installBtn').style.display = 'block';
});

function installApp() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(() => {
      deferredPrompt = null;
      document.getElementById('installBtn').style.display = 'none';
    });
  }
}

// Register Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

function switchTab(type) {
  document.getElementById('setup-form').style.display = type === 'setup' ? 'block' : 'none';
  document.getElementById('analysis-form').style.display = type === 'analysis' ? 'block' : 'none';
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', (type === 'setup' && i === 0) || (type === 'analysis' && i === 1));
  });
}

async function sendSetup() {
  const data = {
    type: 'setup',
    symbol: document.getElementById('s-symbol').value,
    direction: document.getElementById('s-direction').value,
    entry: document.getElementById('s-entry').value,
    sl: document.getElementById('s-sl').value,
    tp1: document.getElementById('s-tp1').value,
    tp2: document.getElementById('s-tp2').value,
    tp3: document.getElementById('s-tp3').value,
    rr: document.getElementById('s-rr').value,
  };
  await sendToServer(data);
}

async function sendAnalysis() {
  const targetsRaw = document.getElementById('a-targets').value;
  const targets = targetsRaw.split('\\n').filter(t => t.trim());
  const data = {
    type: 'analysis',
    symbol: document.getElementById('a-symbol').value,
    trend: document.getElementById('a-trend').value,
    buy_zone: document.getElementById('a-zone').value,
    cancel: document.getElementById('a-cancel').value,
    targets: targets,
    description: document.getElementById('a-desc').value,
  };
  await sendToServer(data);
}

async function sendToServer(data) {
  const status = document.getElementById('status');
  status.className = 'status loading';
  status.innerHTML = '⏳ در حال ارسال...';
  try {
    const res = await fetch('/webhook', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.status === 'ok') {
      status.className = 'status success';
      status.innerHTML = '✅ با موفقیت در کانال نشر شد!';
      // پاک کردن فرم
      setTimeout(() => { status.innerHTML = ''; }, 3000);
    } else {
      status.className = 'status error';
      status.innerHTML = '❌ خطا در ارسال';
    }
  } catch(e) {
    status.className = 'status error';
    status.innerHTML = '❌ خطا در اتصال به سرور';
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def panel():
    return render_template_string(PANEL_HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": str(datetime.now())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
