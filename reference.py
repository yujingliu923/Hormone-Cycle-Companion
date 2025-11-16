# app.py
from datetime import datetime, date, timedelta
from math import exp
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-me'

# ---------------------------
# Helpers: cycle math & hormone estimate
# ---------------------------

def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

def day_in_cycle(last_period_start: date, today: date, cycle_length: int):
    delta = (today - last_period_start).days
    # handle negative (future date) by returning None
    if delta < 0:
        return None
    return (delta % cycle_length) + 1  # 1-indexed

def estimate_phase(cycle_day, cycle_length, menses_days, luteal_length=14):
    # compute ovulation day estimate
    ovulation_day = max(1, cycle_length - luteal_length)
    # define windows
    menses = range(1, menses_days+1)
    follicular = range(menses_days+1, ovulation_day)
    # ovulation window +/-1 day
    ov_start = max(1, ovulation_day-1)
    ov_end = min(cycle_length, ovulation_day+1)
    ovulation = range(ov_start, ov_end+1)
    luteal = range(ov_end+1, cycle_length+1)
    if cycle_day in menses:
        return "Menstruation"
    if cycle_day in ovulation:
        return "Ovulation"
    if cycle_day in luteal:
        return "Luteal"
    return "Follicular"

def gaussian(x, mu, sigma, height=1.0):
    return height * exp(-((x-mu)**2) / (2*sigma*sigma))

def estimate_hormones(cycle_day, cycle_length):
    # simplified: map days to x in [1, cycle_length]
    x = float(cycle_day)
    L = float(cycle_length)
    # estrogen: rises to midcycle peak (~ovulation), smaller luteal plateau
    mu_est = max(2, L - 14)  # roughly ovulation day
    est_peak = gaussian(x, mu_est, sigma=2.0, height=1.0)
    est_luteal = gaussian(x, mu_est + 6, sigma=6.0, height=0.5)
    est_val = max(est_peak, est_luteal)
    # progesterone: low in follicular, rises after ovulation
    mu_prog = mu_est + 5
    prog_val = gaussian(x, mu_prog, sigma=4.0, height=1.0)
    # LH: sharp spike near ovulation
    lh_val = gaussian(x, mu_est, sigma=0.9, height=1.0)
    # testosterone: small increase near ovulation
    t_val = gaussian(x, mu_est, sigma=2.5, height=0.4)
    # normalize to 0-100
    raw = {'estrogen': est_val, 'progesterone': prog_val, 'LH': lh_val, 'testosterone': t_val}
    mx = max(raw.values()) if max(raw.values())>0 else 1.0
    scaled = {k: int(round( (v/mx)*100 )) for k,v in raw.items()}
    return scaled

def symptoms_for_phase(phase):
    mapping = {
        "Menstruation": ["疲倦", "腹痛/痉挛", "烦躁/情绪低落", "对外界敏感度升高"],
        "Follicular": ["能量回升", "注意力改善", "性欲中等", "情绪较为稳定"],
        "Ovulation": ["性欲上升", "自信/社交欲增强", "体力提高", "嗅觉/吸引力感知增强"],
        "Luteal": ["经前情绪波动（易怒/焦虑）", "乳房胀痛", "食欲变化", "睡眠改变"],
    }
    return mapping.get(phase, [])

def advice_for_user(phase, role="self", tone="gentle"):
    # role: 'self' (female user viewing自己), 'partner' (male viewing伴侣)
    # tone: 'gentle' or 'playful'
    adv = []
    if role == "self":
        if phase == "Menstruation":
            adv = [
                "你现在可能比较疲惫 —— 允许自己休息，喝点热饮、热敷下腹可以缓解不适。",
                "如果情绪暴躁，试试 4-4-8 深呼吸（吸气4秒，屏息4秒，呼气8秒）或短时散步。"
            ]
            wrap = "温柔提醒：这是生理周期的一部分，对自己好一点。"
        elif phase == "Ovulation":
            if tone=="playful":
                wrap = "⚡️ 排卵期来了，给自己一点小放纵吧（安全第一）！"
            else:
                wrap = "感觉性欲上升或更自信是常见的 —— 享受但注意安全与共识。"
            adv = ["可以把注意力放在积极社交或亲密互动上。", "如果想，要与伴侣谈清楚界限与保护措施。"]
        elif phase == "Luteal":
            adv = ["尝试规律睡眠与低强度运动（散步/伸展）以稳定情绪。", "若经前情绪严重影响日常，请咨询专业医生。"]
            wrap = "经前期可能更敏感，允许自己放慢节奏。"
        else:
            adv = ["你的身体在恢复与准备下一次排卵，保持饮食均衡有帮助。"]
            wrap = "温和提示：每个人都会有所不同，观察自己的模式很重要。"
        return {"headline": wrap, "items": adv}
    else:
        # partner guidance (简短模板 + 话术)
        if phase in ["Menstruation", "Luteal"]:
            headline = "伴侣可能情绪敏感 — 可用温和、支持的方式。"
            tips = [
                "主动询问需要什么（热水、空间或陪伴），并尊重她的回答。",
                "避免在情绪高涨时争论重大问题；用同理语句开头，例如：'我看到你很累，我在这儿陪你'。"
            ]
            phrases = [
                "“你要不要喝点热水？我去给你倒杯。”",
                "“我能为你做点什么，哪怕只是安静陪着？”"
            ]
        else:
            headline = "伴侣可能精力好/性欲上升 —— 推荐健康、尊重的互动。"
            tips = [
                "保持积极的肢体语言和沟通，确认双方都舒服与同意。",
                "可用俏皮但尊重的邀请语，例如：'今晚想一起做点有趣的事吗？' "
            ]
            phrases = [
                "“你好美/你今天看起来很有魅力。”",
                "“我想和你亲近，想知道你是否也有这个想法？”"
            ]
        return {"headline": headline, "tips": tips, "phrases": phrases}

# ---------------------------
# Routes & templates
# ---------------------------

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CycleBuddy — 激素周期小助手（MVP）</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,"Helvetica Neue",Arial; padding:12px; background:#fff;}
    .card{max-width:720px;margin:8px auto;padding:14px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06)}
    h1{font-size:20px;margin:0 0 8px}
    label{display:block;margin-top:10px;font-weight:600}
    input, select{width:100%;padding:10px;margin-top:6px;border-radius:8px;border:1px solid #ddd}
    button{margin-top:12px;padding:10px 14px;border-radius:10px;border:0;background:#0b84ff;color:white;font-weight:600}
    .result{margin-top:12px;padding:10px;background:#f9f9fb;border-radius:8px}
    .hormone{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
    .h-item{flex:1 1 45%;background:#fff;padding:8px;border-radius:8px;border:1px solid #eee}
    .small{font-size:12px;color:#666}
    .sym{margin-top:8px}
    pre{white-space:pre-wrap;word-break:break-word}
    footer{font-size:12px;color:#888;text-align:center;margin-top:12px}
  </style>
</head>
<body>
  <div class="card">
    <h1>CycleBuddy — 激素周期小助手（MVP）</h1>
    <p class="small">仅作教育/自我觉察用途，非医疗诊断。数据基于平均统计模式，个体差异大。详见下方引用。</p>
    <form id="frm">
      <label>上次月经开始日期</label>
      <input type="date" id="last_date" name="last_date" required>

      <label>平均周期长度（天）</label>
      <input type="number" id="cycle_length" name="cycle_length" placeholder="例如 28" value="28" min="20" max="40">

      <label>经期持续天数（可选）</label>
      <input type="number" id="menses_days" name="menses_days" placeholder="例如 5" value="5" min="1" max="10">

      <label>你/你的角色</label>
      <select id="role" name="role">
        <option value="self">我是想了解自己的（女性）</option>
        <option value="partner">我是男性/想了解伴侣</option>
        <option value="other">其他（仍按女性流程）</option>
      </select>

      <label>语气</label>
      <select id="tone" name="tone">
        <option value="gentle">温和</option>
        <option value="playful">俏皮</option>
      </select>

      <button type="submit">生成评估</button>
    </form>

    <div id="out" class="result" style="display:none"></div>

    <div style="margin-top:10px;font-size:12px;color:#666">
      <strong>重要引用（摘录）</strong>
      <ul>
        <li>周期中位数约 28 天，个体差异显著（22–38 天）。来源：Large cohorts / Nature & Harvard. </li>
        <li>雌激素在接近排卵时达到峰值；孕激素在排卵后（黄体期）上升并于月经前骤降。来源：教科书/StatPearls/NCBI。</li>
        <li>排卵期常见性欲上升，但个体差异大。来源：行为科学研究综述。</li>
      </ul>
    </div>

    <footer>本项目开源，建议仅在本地或私人部署用于自我觉察。如需进一步医疗建议，请咨询专业医生。</footer>
  </div>

<script>
document.getElementById('frm').addEventListener('submit', async function(e){
  e.preventDefault();
  const data = {
    last_date: document.getElementById('last_date').value,
    cycle_length: document.getElementById('cycle_length').value,
    menses_days: document.getElementById('menses_days').value,
    role: document.getElementById('role').value,
    tone: document.getElementById('tone').value
  };
  const res = await fetch('/api/evaluate', {
    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)
  });
  const js = await res.json();
  const out = document.getElementById('out');
  if(js.error){
    out.style.display='block';
    out.innerHTML = '<div style="color:crimson"><strong>错误：</strong>'+js.error+'</div>';
    return;
  }
  out.style.display='block';
  out.innerHTML = `
    <div><strong>今天周期日：</strong>${js.cycle_day} / 周期 ${js.cycle_length} 天</div>
    <div><strong>阶段：</strong>${js.phase}</div>
    <div class="hormone">
      <div class="h-item"><strong>雌激素</strong><div class="small">${js.hormones.estrogen}%</div></div>
      <div class="h-item"><strong>孕激素</strong><div class="small">${js.hormones.progesterone}%</div></div>
      <div class="h-item"><strong>LH</strong><div class="small">${js.hormones.LH}%</div></div>
      <div class="h-item"><strong>睾酮</strong><div class="small">${js.hormones.testosterone}%</div></div>
    </div>
    <div class="sym"><strong>常见症状（这个阶段）</strong>
      <ul>${js.symptoms.map(s=>' <li>'+s+'</li>').join('')}</ul>
    </div>
    <div class="advice"><strong>建议：</strong>
      <div><em>${js.advice.headline || ''}</em></div>
      <ul>${(js.advice.items||js.advice.tips||[]).map(it=>' <li>'+it+'</li>').join('')}</ul>
      ${(js.advice.phrases ? '<div class="small"><strong>示例话术：</strong><ul>'+js.advice.phrases.map(p=>' <li>'+p+'</li>').join('')+'</ul></div>':'')}
    </div>
  `;
});
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    payload = request.get_json() or {}
    last = payload.get("last_date")
    cycle_length = int(payload.get("cycle_length") or 28)
    menses_days = int(payload.get("menses_days") or 5)
    role = payload.get("role") or "self"
    tone = payload.get("tone") or "gentle"
    ld = parse_date(last)
    if not ld:
        return jsonify({"error":"请填写合法的上次月经开始日期（YYYY-MM-DD）。"}), 400
    today = date.today()
    cd = day_in_cycle(ld, today, cycle_length)
    if cd is None:
        return jsonify({"error":"上次月经开始日期不能在未来。"}), 400
    phase = estimate_phase(cd, cycle_length, menses_days)
    hormones = estimate_hormones(cd, cycle_length)
    symptoms = symptoms_for_phase(phase)
    advice = advice_for_user(phase, role=("self" if role=="self" or role=="other" else "partner"), tone=tone)
    return jsonify({
        "cycle_day": cd,
        "cycle_length": cycle_length,
        "phase": phase,
        "hormones": hormones,
        "symptoms": symptoms,
        "advice": advice,
        "today": today.isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)