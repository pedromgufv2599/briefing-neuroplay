import re, json, html
from content import C

def md(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    paras = s.split("\n\n")
    return "".join("<p>" + p.replace("\n", "<br>") + "</p>" for p in paras)

def inline(s):
    s = html.escape(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<em>\1</em>", s)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#222}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;background:#0D0E11;color:#ECEDF1;
 font-family:'Inter';padding:96px 88px 120px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center;font:700 26px 'Inter';letter-spacing:.14em;text-transform:uppercase;color:#8A8D96;margin-bottom:70px}
.top .brand{color:#fff}.top .brand span{color:#FA2F22}
.bot{position:absolute;left:88px;right:88px;bottom:64px;display:flex;justify-content:space-between;align-items:center;font:800 28px 'Inter';letter-spacing:.12em;text-transform:uppercase}
.bot .neutral{color:#6B6E77;font-weight:600;letter-spacing:.06em;font-size:24px}
.bot .swipe{color:#FA2F22}
h2{font:900 40px 'Inter Display';text-transform:uppercase;letter-spacing:.04em;color:#FA2F22;margin-bottom:44px;display:flex;align-items:center;gap:20px}
h2:before{content:"";width:56px;height:8px;background:#FA2F22;display:block}
.body p{font:500 54px/1.28 'Inter';margin-bottom:34px;color:#D9DBE1}
.body b{color:#fff;font-weight:800;background:linear-gradient(transparent 62%, rgba(250,47,34,.55) 62%)}
.body i{font-style:italic;color:#fff}
.cover{background:#0D0E11;color:#fff}
.cover:after{content:"";position:absolute;left:0;right:0;top:0;height:14px;background:#FFD000}
.kicker{align-self:flex-start;background:#FA2F22;color:#fff;font:800 32px 'Inter';letter-spacing:.12em;text-transform:uppercase;padding:16px 28px;margin-bottom:54px;position:relative;transform:rotate(-1.5deg)}
.ctitle{position:relative;display:flex;flex-direction:column;align-items:flex-start}
.cpre,.cpost{font:900 78px/1.02 'Inter Display';text-transform:uppercase;letter-spacing:-.01em;color:#fff}
.cpre{margin-bottom:26px}.cpost{margin-top:26px}
.tarja{display:block;background:#FFD000;color:#0D0E11;font:900 200px/0.98 'Inter Display';text-transform:uppercase;letter-spacing:-.03em;padding:22px 26px 4px;margin:8px 0 8px -26px;white-space:nowrap;transform:rotate(-2deg);box-shadow:12px 12px 0 #FA2F22}
.tarja + .tarja{margin-top:16px}
.csub{margin-top:auto;margin-bottom:64px;font:600 42px/1.25 'Inter';color:#C9CBD2;max-width:880px;position:relative}
.cover .bot .swipe{background:#FFD000;color:#0D0E11;font-size:32px;padding:12px 22px}.cover .bot .neutral{color:#8A8D96}
.ghost{position:absolute;right:-40px;bottom:-110px;font:900 420px/1 'Inter Display';color:rgba(255,255,255,.035);letter-spacing:-.04em}
.boxes{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:10px}
.box{border:3px solid #2A2C33;padding:26px 30px;display:flex;justify-content:space-between;align-items:baseline}
.box span{font:700 30px 'Inter';text-transform:uppercase;letter-spacing:.08em;color:#8A8D96}
.box strong{font:900 72px 'Inter Display';color:#fff}
.pre p{font:500 44px/1.3 'Inter';color:#C9CBD2}
.pre b{color:#fff;font-weight:800}
.bigline{font:900 100px/1.0 'Inter Display';text-transform:uppercase;color:#fff;margin:36px 0 44px;padding:34px 0;border-top:6px solid #FA2F22;border-bottom:6px solid #FA2F22;letter-spacing:-.01em}
.quote .bigline{font:800 72px/1.12 'Inter Display';text-transform:none}
.side .tag{align-self:flex-start;font:900 34px 'Inter Display';letter-spacing:.14em;text-transform:uppercase;padding:14px 26px;margin-bottom:26px}
.sideA .tag{background:#FFD000;color:#0D0E11}
.sideB .tag{background:#2EC4E6;color:#0D0E11}
.side h3{font:900 76px/1.0 'Inter Display';text-transform:uppercase;color:#fff;margin-bottom:56px;letter-spacing:-.01em}
.sideA .body b{background:linear-gradient(transparent 62%, rgba(255,208,0,.5) 62%)}
.sideB .body b{background:linear-gradient(transparent 62%, rgba(46,196,230,.5) 62%)}
.side{border-left:18px solid}
.sideA{border-color:#FFD000}.sideB{border-color:#2EC4E6}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:40px 0 30px}
.stat{background:#17191E;padding:34px 34px 30px;border-top:8px solid #FA2F22}
.stat strong{display:block;font:900 150px/0.9 'Inter Display';color:#fff}
.stat span{font:700 32px 'Inter';text-transform:uppercase;letter-spacing:.08em;color:#8A8D96}
.note p{font:500 34px 'Inter';color:#8A8D96}
.endq{margin-top:auto;background:#FA2F22;color:#0D0E11;padding:44px 48px;margin-bottom:60px}
.endq .lbl{font:800 26px 'Inter';letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px}
.endq .q{font:900 66px/1.02 'Inter Display';text-transform:uppercase}
.endq .c{font:700 32px 'Inter';margin-top:18px}
.src{position:absolute;left:88px;right:88px;bottom:56px;font:500 22px/1.4 'Inter';color:#6B6E77}
.src b{color:#8A8D96}
"""

def top(i, n):
    return f'<div class="top"><div class="brand">Neu Barreiro <span>●</span> Pós-Enem 2026</div><div>{i}/{n}</div></div>'

BOT = '<div class="bot"><div class="neutral">Os dois lados. Você decide.</div><div class="swipe">Arrasta →</div></div>'

def slide(s, i, n):
    t = s["t"]
    e = html.escape
    if t == "cover":
        pre = f'<div class="cpre">{e(s["pre"])}</div>' if s.get("pre") else ""
        post = f'<div class="cpost">{e(s["post"])}</div>' if s.get("post") else ""
        keys = "".join(f'<span class="tarja">{e(k)}</span>' for k in s["key"].split("\n"))
        return (f'<section class="slide cover">{top(i,n)}<div class="ghost">ENEM</div>'
                f'<div class="kicker">{e(s["kicker"])}</div><div class="ctitle">{pre}{keys}{post}</div>'
                f'<div class="csub">{e(s["sub"])}</div>{BOT}</section>')
    if t == "text":
        boxes = ""
        if s.get("boxes"):
            boxes = '<div class="boxes">' + "".join(f'<div class="box"><span>{a}</span><strong>{b}</strong></div>' for a, b in s["boxes"]) + '</div>'
        return f'<section class="slide">{top(i,n)}<h2>{e(s["h"])}</h2><div class="body">{md(s["body"])}</div>{boxes}{BOT}</section>'
    if t in ("big", "quote"):
        pre = f'<div class="pre">{md(s["pre"])}</div>' if s.get("pre") else ""
        return f'<section class="slide {t}">{top(i,n)}<h2>{e(s["h"])}</h2>{pre}<div class="bigline">{e(s["big"])}</div><div class="body">{md(s["body"])}</div>{BOT}</section>'
    if t == "side":
        lbl = "Lado A" if s["side"] == "A" else "Lado B"
        return f'<section class="slide side side{s["side"]}">{top(i,n)}<div class="tag">{lbl}</div><h3>{e(s["h"])}</h3><div class="body">{md(s["body"])}</div>{BOT}</section>'
    if t == "stats":
        st = '<div class="stats">' + "".join(f'<div class="stat"><strong>{b}</strong><span>{a}</span></div>' for a, b in s["stats"]) + '</div>'
        return f'<section class="slide">{top(i,n)}<h2>{e(s["h"])}</h2><div class="pre">{md(s["pre"])}</div>{st}<div class="note">{md(s["body"])}</div>{BOT}</section>'
    if t == "end":
        return (f'<section class="slide">{top(i,n)}<h2>{e(s["h"])}</h2><div class="body">{md(s["body"])}</div>'
                f'<div class="endq"><div class="lbl">Aqui não tem lado. Agora é com você:</div><div class="q">{e(s["q"])}</div>'
                f'<div class="c">Comenta aqui embaixo 👇 e salva este post.</div></div>'
                f'<div class="src"><b>Fontes:</b> {e(s["src"])}</div></section>')

for c in C:
    n = len(c["slides"])
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
           + "".join(slide(s, i + 1, n) for i, s in enumerate(c["slides"])) + '</body></html>')
    open(f'{c["slug"]}.html', 'w').write(doc)
json.dump([c["slug"] for c in C], open("slugs.json", "w"))
print("built")
