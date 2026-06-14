from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# تنظیمات
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7255636020:AAE2uVHWtRWmGl2eXjILnGCCG4hYjKsmOIg")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1003211477952")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ارسال پیام به تلگرام
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def send_telegram(message, photo=None):
    try:
        if photo:
            data = {
                "chat_id": CHANNEL_ID,
                "caption": message,
                "parse_mode": "HTML"
            }
            files = {"photo": photo}
            r = requests.post(TELEGRAM_PHOTO_URL, data=data, files=files)
        else:
            data = {
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            r = requests.post(TELEGRAM_URL, json=data)
        
        return r.status_code == 200
    except Exception as e:
        print(f"خطا: {e}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ساخت پیام تحلیل بازار
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ساخت پیام ستاپ معاملاتی
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_setup_message(data):
    symbol = data.get("symbol", "")
    direction = data.get("direction", "")
    entry = data.get("entry", "")
    sl = data.get("sl", "")
    tp1 = data.get("tp1", "")
    tp2 = data.get("tp2", "")
    tp3 = data.get("tp3", "")
    rr = data.get("rr", "")

    emoji = "🟢" if direction.upper() == "BUY" else "🔴"
    dir_fa = "BUY 📈" if direction.upper() == "BUY" else "SELL 📉"

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Webhook از TradingView
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# پنل ساده ارسال دستی
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PANEL_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kamalhaqjo Signal Panel</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0a; color: #f0f0f0; font-family: Tahoma, sans-serif; padding: 20px; }
  .container { max-width: 600px; margin: 0 auto; }
  h1 { color: #FFD700; text-align: center; margin-bottom: 30px; font-size: 22px; }
  .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
  .tab { flex: 1; padding: 12px; background: #1a1a1a; border: 1px solid #333; border-radius: 8px; 
         cursor: pointer; text-align: center; color: #aaa; transition: all 0.3s; }
  .tab.active { background: #FFD700; color: #000; font-weight: bold; border-color: #FFD700; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 6px; color: #FFD700; font-size: 14px; }
  input, textarea, select { width: 100%; padding: 10px; background: #1a1a1a; border: 1px solid #333;
    border-radius: 8px; color: #f0f0f0; font-size: 14px; font-family: Tahoma; }
  textarea { height: 80px; resize: vertical; }
  .btn { width: 100%; padding: 14px; background: #FFD700; color: #000; border: none;
    border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
  .btn:hover { background: #FFC000; }
  .preview { background: #1a1a1a; border: 1px solid #FFD700; border-radius: 8px; 
    padding: 15px; margin-top: 20px; white-space: pre-wrap; font-size: 13px; line-height: 1.8; }
  .success { color: #00ff88; text-align: center; margin-top: 10px; font-weight: bold; }
  .error { color: #ff4444; text-align: center; margin-top: 10px; }
  .row { display: flex; gap: 10px; }
  .row .form-group { flex: 1; }
</style>
</head>
<body>
<div class="container">
  <h1>🦅 پنل سیگنال Kamalhaqjo</h1>
  
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
  status.innerHTML = '<p style="color:#FFD700;text-align:center">در حال ارسال...</p>';
  try {
    const res = await fetch('/webhook', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.status === 'ok') {
      status.innerHTML = '<p class="success">✅ با موفقیت در کانال نشر شد!</p>';
    } else {
      status.innerHTML = '<p class="error">❌ خطا در ارسال</p>';
    }
  } catch(e) {
    status.innerHTML = '<p class="error">❌ خطا: ' + e + '</p>';
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
