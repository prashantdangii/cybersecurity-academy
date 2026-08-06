#!/usr/bin/env python3
"""Generate remaining Cybersecurity Academy lesson pages + Discord HQ wiring."""
from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
from pathlib import Path

ROOT = Path("/Users/prashantdangi/cybersecurity-academy")
DISCORD = "https://discord.com/channels/1449813215788797954"

CSS = re.search(
    r"(<style>[\s\S]*?</style>)",
    (ROOT / "cybercore/secure-java-development.html").read_text(),
).group(1)

# Extra CSS snippet injected after existing style close — append inside <style> via replace
EXTRA_CSS = """
.ncard.dc{border-color:color-mix(in srgb,var(--accent) 50%,var(--line));background:color-mix(in srgb,var(--accent) 8%,var(--panel))}
.ncard.dc:hover{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 14%,var(--panel-2))}
.unlock{border:1px solid color-mix(in srgb,var(--accent) 40%,var(--line));border-radius:12px;padding:14px 16px;background:color-mix(in srgb,var(--accent) 8%,var(--panel));margin:12px 0}
.unlock .k{font:10px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}
.unlock p{margin:0 0 10px;color:var(--ink-faint);font-size:14px}
.unlock a.btn{display:inline-flex;align-items:center;gap:6px;text-decoration:none}
"""


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


def q(qq, opts):
    """Build a quiz; option order is seeded-shuffled so the correct answer is not always B."""
    items = list(opts)
    rng = random.Random(int(hashlib.sha256(f"mcq-v2:{qq}".encode()).hexdigest()[:16], 16))
    rng.shuffle(items)
    buttons = []
    for item in items:
        if len(item) == 2:
            text, ok = item
            why = "Solid." if ok else "Not quite."
        else:
            text, why, ok = item
        okattr = ' data-ok="1"' if ok else ""
        buttons.append(
            f'<button class="qopt" type="button"{okattr} data-why="{esc_attr(why)}">'
            f'<span class="m"></span><span>{text}</span></button>'
        )
    return (
        '<div class="blk check"><h3>Check yourself</h3><div class="quiz">'
        f'<p class="qq">{qq}</p><div class="qopts">{"".join(buttons)}</div></div></div>'
    )


def lab(tgt, items):
    lis = "".join(
        f'<li><label><input type="checkbox"><span class="b"></span>'
        f'<span class="x">{i}</span></label></li>'
        for i in items
    )
    return (
        f'<div class="blk lab"><h3>Lab</h3><p class="labtgt">Target: <b>{tgt}</b></p>'
        f'<ul class="chk">{lis}</ul></div>'
    )


def term(tid, title, mt, md, tasks, prompt="ops@lab:~$"):
    tlis = "".join(f'<li data-task="{k}">{v}</li>' for k, v in tasks)
    return f'''
<div class="blk"><h3>Mission terminal</h3>
<div class="mission"><span class="kk">Mission</span><span class="t">{mt}</span><span class="d">{md}</span></div>
<div class="termx" data-id="{tid}">
  <div class="th"><span class="traffic"><span class="tb r"></span><span class="tb y"></span><span class="tb g"></span></span>
  <span class="title">{title}</span><span class="tag">live</span></div>
  <div class="termx-screen">
  <div class="termx-out"></div>
  <form class="termx-in"><span class="ps">{prompt}</span>
  <input autocomplete="off" spellcheck="false" aria-label="Terminal input" placeholder="type a command — try help"></form>
  </div>
  <p class="termx-hint" hidden></p>
  <ul class="termx-tasks">{tlis}</ul>
</div></div>'''


def unlock_box(blurb="Daily drills, job alerts, and chapter updates land in Discord."):
    return f'''
<div class="unlock"><span class="k">Open Discord</span>
<p>{blurb}</p>
<a class="btn pri" href="{DISCORD}" target="_blank" rel="noopener noreferrer">Open Discord →</a>
</div>'''


def discord_card(d="Chapter drops · Q&A · check-ins"):
    return (
        f'<a class="ncard dc" href="{DISCORD}" target="_blank" rel="noopener noreferrer">'
        f'<span class="k">Open Discord</span><span class="t">Academy HQ</span>'
        f'<span class="d">{d}</span></a>'
    )


def next_card(href, title, d):
    return (
        f'<a class="ncard" href="{href}"><span class="k">Next</span>'
        f'<span class="t">{title}</span><span class="d">{d}</span></a>'
    )


def prev_card(href, title, d):
    return (
        f'<a class="ncard back" href="{href}"><span class="k">Previous</span>'
        f'<span class="t">{title}</span><span class="d">{d}</span></a>'
    )


def step(n, title, desc, kind, concept, extra=""):
    return f'''
<section class="lesson" data-title="{title}" data-desc="{desc}" hidden>
  <div class="lhead"><span class="n">{n:02d}</span>
  <span><span class="k">{kind}</span><h2>{title}</h2></span></div>
  <div class="blk"><h3>Concept</h3>{concept}</div>
  {extra}
</section>'''


def make_js(key, award_id, badge, xp, termx_literal):
    return f"""
<script>
(function(){{
"use strict";
var PROG_KEY="csa:progress";
var RANKS=[
  {{id:"recruit",name:"Recruit",min:0}},
  {{id:"initiate",name:"Initiate",min:50}},
  {{id:"operator",name:"Operator",min:250}},
  {{id:"ready",name:"Job Ready",min:800}},
  {{id:"specialist",name:"Specialist",min:1400}}
];
var PROG={{xp:0,badges:[],cleared:[],plan:null}};
try{{var pr=localStorage.getItem(PROG_KEY); if(pr) PROG=Object.assign(PROG,JSON.parse(pr));
  if(!Array.isArray(PROG.badges)) PROG.badges=[];
  if(!Array.isArray(PROG.cleared)) PROG.cleared=[];
}}catch(e){{}}
function saveProg(){{try{{localStorage.setItem(PROG_KEY,JSON.stringify(PROG));}}catch(e){{}}}}
function rankOf(xp){{var r=RANKS[0]; for(var i=0;i<RANKS.length;i++) if(xp>=RANKS[i].min) r=RANKS[i]; return r;}}
function nextRank(xp){{for(var i=0;i<RANKS.length;i++) if(RANKS[i].min>xp) return RANKS[i]; return null;}}
function paintHud(flash){{
  var r=rankOf(PROG.xp), n=nextRank(PROG.xp);
  var elR=document.getElementById("hudRank"), elX=document.getElementById("hudXp"),
      elN=document.getElementById("hudNext"), elB=document.getElementById("hudBar"),
      elBadge=document.getElementById("hudBadge");
  if(elR) elR.textContent=r.name;
  if(elX) elX.textContent=String(PROG.xp);
  if(elN) elN.textContent=n?((n.min-PROG.xp)+" to "+n.name):"max rank";
  if(elB){{var lo=r.min, hi=n?n.min:r.min+100; elB.style.width=(n?Math.min(100,((PROG.xp-lo)/(hi-lo))*100):100)+"%";}}
  if(elBadge){{
    if(flash){{elBadge.hidden=false; elBadge.textContent="+ "+flash;}}
    else if(PROG.badges.length){{elBadge.hidden=false; elBadge.textContent=PROG.badges[PROG.badges.length-1];}}
    else elBadge.hidden=true;
  }}
}}
function toast(msg){{
  var t=document.getElementById("xpToast"); if(!t) return;
  t.textContent=msg; t.classList.add("on");
  clearTimeout(toast._t); toast._t=setTimeout(function(){{t.classList.remove("on");}},2200);
}}
function award(levelId,xp,badge){{
  if(PROG.cleared.indexOf(levelId)!==-1){{paintHud(); return false;}}
  PROG.cleared.push(levelId); PROG.xp+=(xp|0);
  if(badge && PROG.badges.indexOf(badge)===-1) PROG.badges.push(badge);
  saveProg(); paintHud(badge||null); toast("+"+xp+" XP"+(badge?" · "+badge:"")); return true;
}}
paintHud();

var intro=document.getElementById("intro");
var fin=document.getElementById("fin");
var steps=[].slice.call(document.querySelectorAll(".lesson[data-title]"));
var screens=[intro].concat(steps,[fin]);
var dotsEl=document.getElementById("dots");
var ctrEl=document.getElementById("ctr");
var prevB=document.getElementById("prev");
var nextB=document.getElementById("next");
var fillEl=document.querySelector(".pbar > i");
var plist=document.getElementById("plist");
var LAST=screens.length-1;
var KEY={json.dumps(key)};
var S={{i:0,done:{{}},labs:{{}},quiz:{{}},term:{{}}}};
try{{var raw=localStorage.getItem(KEY); if(raw) S=Object.assign(S,JSON.parse(raw));}}catch(e){{}}
if(!S.term) S.term={{}};
function save(){{try{{localStorage.setItem(KEY,JSON.stringify(S));}}catch(e){{}}}}

steps.forEach(function(s,i){{
  s.id="s"+(i+1);
  var b=document.createElement("li");
  b.className="pitem"; b.setAttribute("role","button"); b.tabIndex=0;
  b.innerHTML='<span><span class="t"></span><span class="d"></span></span><span class="go">→</span>';
  b.querySelector(".t").textContent=s.getAttribute("data-title")||("Step "+(i+1));
  b.querySelector(".d").textContent=s.getAttribute("data-desc")||"";
  function go(){{show(i+1);}}
  b.addEventListener("click",go);
  b.addEventListener("keydown",function(e){{if(e.key==="Enter"||e.key===" "){{e.preventDefault();go();}}}});
  if(plist) plist.appendChild(b);
}});
steps.forEach(function(s,i){{
  var d=document.createElement("button");
  d.className="dot"; d.type="button";
  d.title=(i+1)+". "+(s.getAttribute("data-title")||"");
  d.setAttribute("aria-label",d.title);
  d.addEventListener("click",function(){{show(i+1);}});
  dotsEl.appendChild(d);
}});

var cur=0;
function toTop(){{ try{{window.scrollTo(0,0);return;}}catch(e){{}} try{{document.querySelector(".rail").scrollIntoView({{block:"start"}});}}catch(e){{}} }}
function paint(){{
  steps.forEach(function(s,i){{
    var d=dotsEl.children[i];
    var state=S.done[s.id]?"done":"";
    if(cur===i+1) state="active";
    if(d) d.setAttribute("data-state",state);
    var pi=plist&&plist.children[i];
    if(pi) pi.classList.toggle("done",!!S.done[s.id]);
  }});
  var done=steps.filter(function(s){{return S.done[s.id];}}).length;
  if(fillEl) fillEl.style.width=(done/steps.length*100)+"%";
  if(cur===0) ctrEl.innerHTML="Intro";
  else if(cur===LAST) ctrEl.innerHTML="<b>Done</b>";
  else ctrEl.innerHTML="Step <b>"+cur+"</b>/"+steps.length;
  var fs=document.getElementById("finSteps");
  if(fs){{
    fs.textContent=done+"/"+steps.length;
    var labEl=document.getElementById("finLabs");
    var quizEl=document.getElementById("finQuiz");
    if(labEl && typeof boxes!=="undefined") labEl.textContent=boxes.filter(function(b){{return b.checked;}}).length+"/"+boxes.length;
    if(quizEl && typeof quizzes!=="undefined") quizEl.textContent=Object.keys(S.quiz).filter(function(k){{return S.quiz[k].ok;}}).length+"/"+quizzes.length;
  }}
}}
function show(i,noScroll){{
  cur=Math.max(0,Math.min(LAST,i));
  screens.forEach(function(sc,k){{ if(sc) sc.hidden=(k!==cur); }});
  prevB.hidden=(cur===0);
  nextB.hidden=false;
  if(cur===0){{ nextB.textContent=steps.length?"Start → Mission 1":"Start"; }}
  else if(cur===LAST){{ nextB.hidden=true; try{{award({json.dumps(award_id)},{xp},{json.dumps(badge)});}}catch(e){{}} }}
  else {{ nextB.textContent=(cur===steps.length)?"Finish ✓":"Next →"; }}
  S.i=cur; save(); paint();
  try{{history.replaceState(null,"",cur===0?"#":("#"+(cur===LAST?"done":"s"+cur)));}}catch(e){{}}
  if(!noScroll) toTop();
}}
nextB.addEventListener("click",function(){{
  if(cur>=1&&cur<=steps.length){{ S.done[steps[cur-1].id]=1; save(); }}
  show(cur+1);
}});
prevB.addEventListener("click",function(){{show(cur-1);}});
document.addEventListener("keydown",function(e){{
  if(document.activeElement && /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
  if(e.key==="ArrowRight" && nextB && !nextB.hidden) nextB.click();
  if(e.key==="ArrowLeft"&&cur>0) show(cur-1);
}});
var rs=document.getElementById("restart");
if(rs) rs.addEventListener("click",function(e){{e.preventDefault(); show(0);}});

function esc(s){{return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}}
function norm(s){{return String(s||"").trim().replace(/\\s+/g," ").toLowerCase();}}

var boxes=[].slice.call(document.querySelectorAll("ul.chk input[type=checkbox]"));
boxes.forEach(function(cb,i){{
  var id="L"+i; cb.checked=!!S.labs[id];
  cb.addEventListener("change",function(){{ if(cb.checked) S.labs[id]=1; else delete S.labs[id]; save(); paint(); }});
}});

var quizzes=[].slice.call(document.querySelectorAll(".quiz"));
quizzes.forEach(function(q,qi){{
  var id="Q"+qi; var opts=[].slice.call(q.querySelectorAll(".qopt"));
  var fb=document.createElement("div"); fb.className="qfb"; fb.hidden=true; q.appendChild(fb);
  function answer(idx,silent){{
    var o=opts[idx]; if(!o) return;
    var ok=o.getAttribute("data-ok")==="1";
    opts.forEach(function(x){{x.classList.remove("ok","no","reveal");}});
    o.classList.add(ok?"ok":"no");
    if(!ok) opts.forEach(function(x){{if(x.getAttribute("data-ok")==="1") x.classList.add("reveal");}});
    fb.hidden=false; fb.className="qfb "+(ok?"good":"bad");
    fb.innerHTML="<b>"+(ok?"Correct. ":"Not quite. ")+"</b>"+(o.getAttribute("data-why")||"");
    if(!ok){{var right=opts.filter(function(x){{return x.getAttribute("data-ok")==="1";}})[0];
      if(right) fb.innerHTML+=" <b>The answer:</b> "+right.querySelector("span:last-child").textContent+" — "+(right.getAttribute("data-why")||"");}}
    if(!silent){{S.quiz[id]={{i:idx,ok:ok?1:0}}; save(); paint();}}
  }}
  opts.forEach(function(o,i){{o.addEventListener("click",function(){{answer(i);}});}});
  if(S.quiz[id]) answer(S.quiz[id].i,true);
}});

function markTasks(id, conf, c, taskEls){{
  Object.keys(conf.tasks||{{}}).forEach(function(tid){{
    if((conf.tasks[tid]||[]).map(norm).indexOf(c)!==-1){{
      S.term[id].done[tid]=1; save();
      if(taskEls[tid]) taskEls[tid].classList.add("done");
    }}
  }});
}}

var TERMX={termx_literal};
document.querySelectorAll(".termx").forEach(function(box){{
  var id=box.getAttribute("data-id");
  var conf=TERMX[id]; if(!conf) return;
  var out=box.querySelector(".termx-out");
  var form=box.querySelector(".termx-in");
  var input=form.querySelector("input");
  var hint=box.querySelector(".termx-hint");
  var ps=box.querySelector(".ps");
  var taskEls={{}};
  box.querySelectorAll(".termx-tasks [data-task]").forEach(function(li){{ taskEls[li.getAttribute("data-task")]=li; }});
  if(!S.term[id]) S.term[id]={{done:{{}}}};
  Object.keys(S.term[id].done||{{}}).forEach(function(t){{ if(taskEls[t]) taskEls[t].classList.add("done"); }});
  function write(html, cls){{
    var line=document.createElement("div");
    if(cls) line.className=cls;
    line.innerHTML=html;
    out.appendChild(line);
    out.scrollTop=out.scrollHeight;
  }}
  write((conf.welcome||"").replace(/\\n/g,"<br>"));
  form.addEventListener("submit",function(e){{
    e.preventDefault();
    var raw=input.value; var c=norm(raw); input.value="";
    if(!c) return;
    write('<span class="cmd">'+esc(ps.textContent)+" "+esc(raw)+'</span>');
    if(c==="help"){{ write(conf.help||"Type checklist commands.","ok"); return; }}
    if(c==="clear"){{ out.innerHTML=""; write((conf.welcome||"").replace(/\\n/g,"<br>")); return; }}
    var resp=null;
    Object.keys(conf.cmds||{{}}).forEach(function(k){{ if(norm(k)===c) resp=conf.cmds[k]; }});
    if(resp==null){{
      write("command not found — try <span class=\\"hi\\">help</span>","err");
      if(hint){{ hint.hidden=false; hint.textContent="Hint: type help"; }}
      return;
    }}
    write(String(resp).replace(/\\n/g,"<br>"),"ok");
    markTasks(id,conf,c,taskEls);
    if(hint) hint.hidden=true;
  }});
}});

(function init(){{
  var h=location.hash.slice(1);
  if(h==="done") return show(LAST,true);
  var m=/^s(\\d+)$/.exec(h);
  if(m) return show(parseInt(m[1],10),true);
  show(S.i||0,true);
}})();
}})();
</script>
"""


def write_page(
    rel,
    track,
    title,
    crumb,
    lede,
    ocs,
    tags,
    missions,
    fin_cards,
    key,
    award,
    badge,
    termx,
    xp=100,
    footer="Cybersecurity Academy · Authorized labs only",
    legal="Authorized targets only — your lab, intentionally vulnerable apps, in-scope programs, or employer-approved work.",
):
    css = CSS.replace("</style>", EXTRA_CSS + "\n</style>")
    meta = "".join(f'<li class="oc">{x}</li>' for x in ocs) + "".join(
        f'<li class="tag">{x}</li>' for x in tags
    )
    body = f"""
<div class="pbar" aria-hidden="true"><i></i></div>
<div class="xptoast" id="xpToast" role="status" aria-live="polite"></div>
<div class="wrap">
<nav class="rail" aria-label="Lesson progress">
  <div class="in"><span class="ct" id="ctr">Intro</span><div class="dots" id="dots"></div>
  <a class="home" href="../start-here.html">↩ map</a></div>
</nav>
<div class="hud" id="hud"><span class="rank" id="hudRank">Recruit</span>
  <div class="xpwrap"><div class="xpmeta"><span>XP <b id="hudXp">0</b></span><span id="hudNext">—</span></div>
  <div class="xpbar"><i id="hudBar"></i></div></div>
  <span class="badge" id="hudBadge" hidden></span></div>
<section class="lesson" id="intro">
  <header class="page">
    <p class="crumb">~ <b>{crumb}</b></p>
    <h1 class="title">{title}</h1>
    <p class="lede">{lede}</p>
    <ul class="meta">{meta}</ul>
  </header>
  <h2 class="slabel">The path</h2>
  <ul class="plist" id="plist"></ul>
  <div class="note legal"><span class="lb">Rule</span>
    <p><b>{legal}</b></p>
  </div>
  {unlock_box("Missions live on this page. Open Discord for chapter drops, daily drills, and job channels.")}
</section>
{missions}
<section class="lesson" id="fin" hidden>
  <div class="fin"><div class="ring">✓</div>
    <h2>Level clear — {title}</h2>
    <p>Save proof in <code class="inl">lab-notes.md</code>. Continue in Discord for updates, drills, and the next chapter drops.</p>
    <div class="tiles c3" style="text-align:left;margin-bottom:22px">
      <div class="tile acc"><span class="v" id="finSteps">—</span><span class="l">steps done</span></div>
      <div class="tile"><span class="v" id="finLabs">0/0</span><span class="l">lab tasks</span></div>
      <div class="tile"><span class="v" id="finQuiz">0/0</span><span class="l">checks passed</span></div>
    </div>
    <div class="ncards">
      {fin_cards}
      {discord_card()}
      <a class="ncard back" href="../start-here.html"><span class="k">Back to</span><span class="t">Your campaign</span><span class="d">Roadmap.</span></a>
      <a class="ncard back" href="#" id="restart"><span class="k">Or</span><span class="t">Replay</span><span class="d">Any mission.</span></a>
    </div>
  </div>
</section>
<div class="lnav"><div class="in">
  <button class="btn ghost" id="prev" type="button">← Back</button><span class="sp"></span>
  <button class="btn pri" id="next" type="button">Start →</button>
</div></div>
<footer class="page">{footer}</footer>
</div>
"""
    html = f"""<!DOCTYPE html>
<html lang="en" data-track="{track}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Cybersecurity Academy</title>
<meta name="description" content="{title} — Cybersecurity Academy interactive level.">
{css}
</head>
<body>
{body}
{make_js(key, award, badge, xp, termx)}
</body>
</html>
"""
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    script = html.split("<script>")[1].split("</script>")[0]
    Path("/tmp/fullcheck.js").write_text(script)
    r = subprocess.run(["node", "--check", "/tmp/fullcheck.js"], capture_output=True, text=True)
    ok = r.returncode == 0
    print(("OK" if ok else "FAIL"), rel, path.stat().st_size)
    if not ok:
        print(r.stderr[:500])
    return ok


def tjson(obj: dict) -> str:
    """Serialize TERMX with newlines as \\n for JS string friendliness."""
    return json.dumps(obj, ensure_ascii=False)


# =============================================================================
# PAGE BUILDERS — compact mission packs
# =============================================================================

def pack_missions(items):
    """items: list of (title, desc, kind, concept_html, extra_html) — extra optional."""
    out = ""
    for i, item in enumerate(items, 1):
        if len(item) == 4:
            title, desc, kind, concept = item
            extra = ""
        else:
            title, desc, kind, concept, extra = item
        out += step(i, title, desc, kind, concept, extra)
    return out


results = []

# ---------- CAREER ----------
results.append(
    write_page(
        "career/resume-portfolio.html",
        "career",
        "Resume & portfolio for cyber roles",
        "career / resume // job gate · level 1",
        "Turn labs into hire-me proof: resume bullets, portfolio writeups, and a Discord-ready intro.",
        ["→ Jobs", "→ Interviews"],
        ["6 missions", "~3 hrs", "+100 XP"],
        pack_missions(
            [
                (
                    "Role targeting",
                    "Pick the lane",
                    "concept · check",
                    "<p>One resume ≠ every role. Target <b>SOC</b>, <b>AppSec</b>, <b>pentester</b>, or <b>GRC</b> — mirror their language.</p>"
                    '<div class="tiles c3"><div class="tile acc"><span class="v">1</span><span class="l">primary role</span></div>'
                    '<div class="tile"><span class="v">3</span><span class="l">proof projects</span></div>'
                    '<div class="tile"><span class="v">Discord</span><span class="l">job alerts</span></div></div>',
                    q(
                        "Best resume strategy?",
                        [
                            ("One generic CV for all cyber jobs", "Dilutes signal.", False),
                            ("Primary role + mirrored keywords from 3 JDs", "Targeted and scannable.", True),
                            ("Only list tools with no outcomes", "Hiring managers want impact.", False),
                        ],
                    ),
                ),
                (
                    "Impact bullets",
                    "Show results",
                    "concept · lab · check",
                    "<p>Formula: <b>Action + scope + metric/result</b>. Lab work counts if you state the finding class and fix.</p>"
                    '<pre class="code" data-lang="txt"><code>Identified IDOR on invoice API in lab → drafted ownership check + report template</code></pre>',
                    lab(
                        "Your notes / resume draft",
                        [
                            "Rewrite 3 bullets with Action → Result.",
                            "Cut fluff adjectives (passionate, hardworking).",
                            "Add one link/path to a writeup or GitHub.",
                        ],
                    )
                    + q(
                        "Weakest bullet?",
                        [
                            ("Responsible for security stuff", "Vague, no proof.", True),
                            ("Found reflected XSS in Juice Shop; wrote CSP fix note", "Concrete proof.", False),
                            ("Built a homelab SOC with Suricata + Elastic", "Solid project signal.", False),
                        ],
                    ),
                ),
                (
                    "Portfolio writeups",
                    "Public proof",
                    "concept · terminal · lab · check",
                    "<p>Publish <b>sanitized</b> writeups: goal → steps → evidence → fix. Never leak real client data.</p>",
                    term(
                        "folio",
                        "bash · portfolio",
                        "Scaffold a writeup",
                        "Type scaffold then publish",
                        [
                            ("sc", 'Create outline (<code class="inl">scaffold</code>)'),
                            ("pub", 'Publish checklist (<code class="inl">publish</code>)'),
                        ],
                        "writer@folio:~$",
                    )
                    + lab(
                        "GitHub / blog / Notion public page",
                        [
                            "Create one writeup from a cleared academy lab.",
                            "Redact secrets / real hosts.",
                            "Add README index linking 2–3 writeups.",
                        ],
                    )
                    + q(
                        "Portfolio writeups must…",
                        [
                            ("Include production customer PII", "Never — sanitize.", False),
                            ("Be reproducible enough to prove skill without leaking secrets", "Proof + ethics.", True),
                            ("Only list tool names", "Too thin.", False),
                        ],
                    ),
                ),
                (
                    "GitHub & LinkedIn",
                    "Signal channels",
                    "concept · lab · check",
                    "<p>GitHub: clean repos + READMEs. LinkedIn: headline = role target, About = stack + proof links.</p>",
                    lab(
                        "Your profiles",
                        [
                            "Set LinkedIn headline to target role.",
                            "Pin 1 portfolio repo.",
                            "Add academy badge/XP screenshot (optional) to About.",
                        ],
                    )
                    + q(
                        "LinkedIn headline should…",
                        [
                            ("Say Open to work only", "Add role + skills.", False),
                            ("Name the target role + 2–3 skills", "Clear recruiter scan.", True),
                            ("Be blank", "Wasted real estate.", False),
                        ],
                    ),
                ),
                (
                    "Discord job lounge",
                    "Apply where hiring happens",
                    "concept · check",
                    "<p>Job Ready means: Core + track done + resume/portfolio. Apply in Discord — mentors and job posts live there.</p>"
                    + unlock_box("Post intros, get reviews, and track jobs in Discord."),
                    q(
                        "After Job Ready, where do you apply first in this academy?",
                        [
                            ("Random cold DMs with no proof", "Low signal.", False),
                            ("Discord job / intro channels with portfolio links", "Ops home.", True),
                            ("Skip community forever", "Misses the gate.", False),
                        ],
                    ),
                ),
                (
                    "Ship checklist",
                    "Ready to send",
                    "concept · lab · check",
                    "<p>Before apply: PDF resume, 2 writeups, GitHub link, 30-sec Discord intro copied from Start Here.</p>",
                    lab(
                        "Apply pack",
                        [
                            "Export 1-page PDF resume.",
                            "Copy Discord intro + attach 2 links.",
                            "Join Discord and post in the intro channel.",
                        ],
                    )
                    + q(
                        "Minimum apply pack?",
                        [
                            ("Resume + proof links + Discord intro", "Complete signal.", True),
                            ("Only a selfie", "Not evidence.", False),
                            ("Unfinished CTF folder dump", "Noise without narrative.", False),
                        ],
                    ),
                ),
            ]
        ),
        next_card("interview-prep.html", "Interview prep", "Behavioral · technical · labs.")
        + prev_card("../penetration-testing/evasion-techniques-breach.html", "Evasion & breach", "Offense finale."),
        "csa:career/resume-portfolio.html",
        "career/resume-portfolio",
        "job-resume",
        tjson(
            {
                "folio": {
                    "welcome": "Portfolio scaffolder.\\n",
                    "help": "scaffold | publish | clear",
                    "cmds": {
                        "scaffold": "Created writeup.md\\n# Title\\n## Goal\\n## Steps\\n## Evidence\\n## Fix",
                        "publish": "Checklist: sanitize → push → link from README → share in Discord.",
                    },
                    "tasks": {"sc": ["scaffold"], "pub": ["publish"]},
                }
            }
        ),
        xp=100,
        footer="Career · Job Ready gate",
        legal="Never publish real client secrets. Sanitize every writeup.",
    )
)

results.append(
    write_page(
        "career/interview-prep.html",
        "career",
        "Interview prep",
        "career / interviews // job gate · level 2",
        "Practice stories, whiteboard threats, and live lab talk — then run mocks in Discord.",
        ["→ Jobs"],
        ["6 missions", "~3 hrs", "+100 XP"],
        pack_missions(
            [
                (
                    "STAR stories",
                    "Behavioral ammo",
                    "concept · lab · check",
                    "<p><b>STAR</b>: Situation → Task → Action → Result. Prep 5 stories: conflict, failure, leadership, deep work, ethics.</p>",
                    lab(
                        "Notes",
                        [
                            "Write 5 STAR bullets (1 line each).",
                            "Include one ethics / scope story.",
                            "Practice aloud once.",
                        ],
                    )
                    + q(
                        "STAR stands for…",
                        [
                            ("Scan Tools And Run", "No.", False),
                            ("Situation, Task, Action, Result", "Behavioral standard.", True),
                            ("SQL Tables Are Relational", "Unrelated.", False),
                        ],
                    ),
                ),
                (
                    "Technical depth",
                    "Explain like a hire",
                    "concept · terminal · check",
                    "<p>Be ready to explain one web bug, one network concept, and one detection idea end-to-end.</p>",
                    term(
                        "talk",
                        "bash · interview",
                        "Drill explanations",
                        "Type xss then detect",
                        [
                            ("x", 'Explain XSS (<code class="inl">xss</code>)'),
                            ("d", 'Explain detection (<code class="inl">detect</code>)'),
                        ],
                        "candidate@mock:~$",
                    )
                    + q(
                        "Strong technical answer includes…",
                        [
                            ("Only tool names", "Shallow.", False),
                            ("Concept → exploit path → impact → fix/detect", "Shows judgment.", True),
                            ("Memorized CVE list only", "Lists ≠ understanding.", False),
                        ],
                    ),
                ),
                (
                    "Whiteboard / threat model",
                    "Think out loud",
                    "concept · lab · check",
                    "<p>Draw: user → app → DB → IdP. Ask assets, trust boundaries, top 3 risks, controls.</p>",
                    lab(
                        "Paper or Excalidraw",
                        [
                            "Threat-model a login + API app in 10 minutes.",
                            "List 3 risks + 3 controls.",
                            "Record yourself explaining once.",
                        ],
                    )
                    + q(
                        "Threat modeling starts with…",
                        [
                            ("Buying more tools", "Process before shopping.", False),
                            ("Assets, actors, trust boundaries", "Foundation.", True),
                            ("Skipping to exploits", "You miss context.", False),
                        ],
                    ),
                ),
                (
                    "Live lab talk",
                    "Show the work",
                    "concept · check",
                    "<p>Walk a finding: request, response, impact, remediation. Interviewers love calm narration.</p>",
                    q(
                        "During a live demo, if stuck you should…",
                        [
                            ("Panic-mute forever", "Communicate.", False),
                            ("Narrate hypothesis, try next check, ask clarifying Qs", "Shows process.", True),
                            ("Guess randomly without speaking", "Opaque.", False),
                        ],
                    ),
                ),
                (
                    "Mock interviews",
                    "Practice together",
                    "concept · check",
                    "<p>Mock loops happen in Discord — book reviews, peer practice, hiring office hours.</p>"
                    + unlock_box("Practice interviews and get feedback in Discord."),
                    q(
                        "Best place for academy mock interviews?",
                        [
                            ("Discord (Academy HQ)", "That's the ops home.", True),
                            ("Nowhere — wing it", "Practice beats winging.", False),
                            ("Only after 10 years experience", "Practice early.", False),
                        ],
                    ),
                ),
                (
                    "Offer & ethics",
                    "Close clean",
                    "concept · check",
                    "<p>Ask scope of role, on-call, tooling. Never claim unauthorized hacks as experience.</p>",
                    q(
                        "Claiming unauthorized hacks in interviews is…",
                        [
                            ("Impressive", "It's a liability red flag.", False),
                            ("A serious ethics/legal red flag", "Don't.", True),
                            ("Required", "No.", False),
                        ],
                    ),
                ),
            ]
        ),
        next_card("certification-roadmap.html", "Certification roadmap", "What to take · when.")
        + prev_card("resume-portfolio.html", "Resume & portfolio", "Proof pack."),
        "csa:career/interview-prep.html",
        "career/interview-prep",
        "job-interview",
        tjson(
            {
                "talk": {
                    "welcome": "Mock interview drill.\\n",
                    "help": "xss | detect | clear",
                    "cmds": {
                        "xss": "XSS: untrusted input executes in browser → session/actions risk → encode + CSP.",
                        "detect": "Detection: log auth failures + rare dests; alert on beacon-like intervals.",
                    },
                    "tasks": {"x": ["xss"], "d": ["detect"]},
                }
            }
        ),
        xp=100,
        footer="Career · Job Ready gate",
    )
)

results.append(
    write_page(
        "career/certification-roadmap.html",
        "career",
        "Certification roadmap",
        "career / certs // job gate · level 3",
        "Pick certs that match your lane — proof > logos. Study groups live in Discord.",
        ["→ Jobs", "→ Specialist"],
        ["5 missions", "~2 hrs", "+100 XP"],
        pack_missions(
            [
                (
                    "Certs vs skills",
                    "Order of operations",
                    "concept · check",
                    "<p>Labs + portfolio first. Certs amplify a lane; they don't replace proof.</p>",
                    q(
                        "Best order?",
                        [
                            ("Buy every cert then learn", "Wasteful.", False),
                            ("Build skills/portfolio, then pick 1–2 lane certs", "Signal + ROI.", True),
                            ("Skip all learning for dumps", "Unethical and fails interviews.", False),
                        ],
                    ),
                ),
                (
                    "Offense lane",
                    "Pentest / AppSec",
                    "concept · check",
                    "<p>Common path: Security+ (optional) → PNPT/eJPT → OSCP/BSCP lane as skills mature. Match JD language.</p>",
                    q(
                        "OSCP-style certs mainly prove…",
                        [
                            ("Excel macros only", "No.", False),
                            ("Hands-on offensive methodology under pressure", "Lab exam culture.", True),
                            ("GRC policy writing", "Wrong lane.", False),
                        ],
                    ),
                ),
                (
                    "Defense / GRC lanes",
                    "Blue & governance",
                    "concept · check",
                    "<p>Defense: CySA+/BTL1-style → SIEM labs. GRC: Security+ / ISO lead / CISA-ish paths + audit projects.</p>",
                    q(
                        "GRC candidates should emphasize…",
                        [
                            ("Kernel exploits only", "Wrong signal.", False),
                            ("Frameworks, risk process, audit evidence", "Lane fit.", True),
                            ("Only FPS gaming rank", "Irrelevant.", False),
                        ],
                    ),
                ),
                (
                    "Study plan",
                    "Ship a schedule",
                    "concept · lab · check",
                    "<p>8-week blocks: content → labs → practice exams → review weak domains.</p>",
                    lab(
                        "Calendar",
                        [
                            "Pick one target cert (or none — portfolio path).",
                            "Block 3 weekly study slots.",
                            "Join Discord study channel.",
                        ],
                    )
                    + unlock_box("Study groups and accountability streaks live in Discord.")
                    + q(
                        "A good study plan includes…",
                        [
                            ("Only watching videos", "Need labs/practice.", False),
                            ("Labs + spaced review + practice tests", "Retention.", True),
                            ("Cram night before only", "Fragile.", False),
                        ],
                    ),
                ),
                (
                    "Next trees",
                    "After Job Ready",
                    "concept · check",
                    "<p>Gate cleared → choose Bug Bounty, Freelance, Defense deepening, AI, or Vuln Research.</p>",
                    q(
                        "After Job Ready you should…",
                        [
                            ("Stop learning", "Keep leveling.", False),
                            ("Pick an Act 3 tree while applying", "Parallel progress.", True),
                            ("Only farm XP without goals", "Aimless.", False),
                        ],
                    ),
                ),
            ]
        ),
        next_card("../bug-bounty/bug-bounty-fundamentals.html", "Bug bounty fundamentals", "Act 3 · side income.")
        + next_card("../defensive-security/soc-analyst-fundamentals.html", "SOC fundamentals", "Defense track.")
        + prev_card("interview-prep.html", "Interview prep", "Stories · mocks."),
        "csa:career/certification-roadmap.html",
        "career/certification-roadmap",
        "job-certs",
        "{}",
        xp=100,
        footer="Career · Job Ready gate",
    )
)

print("Career done:", sum(1 for x in results if x), "/", len(results))
Path("/tmp/gen_full_state.json").write_text(json.dumps({"n": len(results), "ok": all(results)}))
print("STATE", all(results))

# ---------- BUG BOUNTY ----------
results.append(write_page(
"bug-bounty/bug-bounty-fundamentals.html","bounty","Bug bounty fundamentals",
"bounty / fundamentals // act 3 · level 1",
"Platforms, scope, duplicates, and ethics — hunt only in-scope assets.",
["→ Bounty","→ Income"],["6 missions","~3 hrs","+100 XP"],
pack_missions([
("Platforms & programs","Where to hunt","concept · check",
"<p>HackerOne, Bugcrowd, Intigriti, private programs. Read policy: scope, payouts, safe harbor.</p>",
q("First thing on a new program?",[("Spray every host you can find","Scope first.",False),("Read policy & asset scope carefully","Avoid OOS/ban.",True),("Ignore rate limits","Gets you blocked.",False)])),
("Scope mastery","In vs out","concept · lab · check",
"<p>*.example.com ≠ example.net. Exclusions matter. When unsure → ask via platform.</p>",
lab("A public program policy",[
"List 3 in-scope assets.",
"List 2 exclusions.",
"Note reporting channel & SLA.",
])+q("Out-of-scope testing is…",[("Fine if severity high","Still unauthorized.",False),("A program violation / legal risk","Stay in scope.",True),("Required","No.",False)])),
("Duplicates & noise","Signal over spam","concept · check",
"<p>Check known issues, recent reports culture, and whether your impact is unique.</p>",
q("High duplicate rate usually means…",[("You should report identical noise faster","Wastes triage.",False),("Improve recon uniqueness & impact clarity","Quality > quantity.",True),("Programs hate money","No.",False)])),
("Severity & CVSS-ish","Think impact","concept · terminal · check",
"<p>Impact drives payout: RCE/auth bypass ≫ self-XSS. Explain business risk, not just CVSS theater.</p>",
term("sev","bash · severity","Rank impact","Type impact then payout",[
("i",'State impact (<code class="inl">impact</code>)'),
("p",'Think payout (<code class="inl">payout</code>)'),
],"hunter@bb:~$")+q("Self-XSS typically…",[("Pays like RCE","Usually low/informational.",False),("Is low value without an escalation chain","Needs real victim impact.",True),("Is always critical","No.",False)])),
("Safe hunting habits","Don't burn the program","concept · check",
"<p>Throttle, avoid DoS, no social engineering unless allowed, no data exfil beyond PoC.</p>"+unlock_box("Share hunts (in-scope) and tips in Discord bounty channels."),
q("During bounty testing you should…",[("Dump full customer DBs","Excessive & banned.",False),("Minimize data access to prove impact","Ethics + policy.",True),("Hit production with stress tests","Often forbidden.",False)])),
("Workflow setup","Your hunt kit","concept · lab · check",
"<p>Notes template, Burp project, wordlists, VPN/VPS hygiene, Discord accountability.</p>",
lab("Your machine",[
"Create a bounty notes template.",
"Separate browser profile for hunting.",
"Join Discord bounty channel.",
])+q("Separate browser profiles help…",[("Nothing","Isolation & cookies.",False),("Isolate sessions/extensions per program","Hygiene.",True),("Increase CVSS","No.",False)])),
]),
next_card("recon-asset-discovery.html","Recon & asset discovery","Subdomains · ports · sprawl.")
+prev_card("../career/certification-roadmap.html","Certification roadmap","Job gate."),
"csa:bug-bounty/bug-bounty-fundamentals.html","bounty/fundamentals","bb-fundamentals",
tjson({"sev":{"welcome":"Severity coach.\\n","help":"impact | payout | clear",
"cmds":{"impact":"Ask: who is affected? auth needed? data sensitivity? chainable?",
"payout":"Critical auth bypass / RCE ≫ reflective self-XSS. Write business impact."},
"tasks":{"i":["impact"],"p":["payout"]}}}),
xp=100,footer="Bug Bounty · In-scope only"))

results.append(write_page(
"bug-bounty/recon-asset-discovery.html","bounty","Recon & asset discovery",
"bounty / recon // act 3 · level 2",
"Find forgotten assets — the bugs hide in sprawl.",
["→ Bounty"],["6 missions","~5 hrs","+100 XP"],
pack_missions([
("Asset inventory","Know the estate","concept · check",
"<p>Roots → subs → IPs → apps → APIs. Tag in-scope only.</p>",
q("Recon goal?",[("Attack random internet","Illegal.",False),("Map in-scope attack surface thoroughly","Then prioritize.",True),("Only Google the homepage","Too shallow.",False)])),
("Subdomain discovery","Expand carefully","concept · terminal · lab · check",
"<p>Passive first (CT logs, DNS), then active enum within rules.</p>",
term("recon","bash · recon","Enumerate lab target","Type subs then httpx",[
("s",'Subdomains (<code class="inl">subs</code>)'),
("h",'Probe HTTP (<code class="inl">httpx</code>)'),
],"recon@bb:~$")+lab("In-scope lab/root you own or program allows",[
"Collect passive subs list.",
"Probe live HTTP(S).",
"Note one interesting forgotten host.",
])+q("Prefer passive recon first because…",[("It's slower always","Often quieter / safer start.",False),("Lower noise & respects many program norms","Then active carefully.",True),("Passive finds zero-days only","No.",False)])),
("Content & parameter discovery","Hidden doors","concept · lab · check",
"<p>Dirs, JS secrets, API routes, old backups — still in scope rules.</p>",
lab("One live in-scope host",[
"Crawl / map with a proxy.",
"Review JS for endpoints.",
"Fuzz a small wordlist on one path.",
])+q("JS files often reveal…",[("Nothing useful","Often endpoints/keys.",False),("Hidden API routes & configs","Gold for hunters.",True),("Only CSS colors","No.",False)])),
("Cloud & misc sprawl","Buckets & panels","concept · check",
"<p>Public buckets, staging, admin panels, third-party SaaS connected to brand.</p>",
q("Staging environments are…",[("Always out of scope","Check policy — often juicy if in-scope.",False),("High-value if in-scope (weaker controls)","Weaker controls, still must be in-scope.",True),("Illegal to mention","Report via platform if in policy.",False)])),
("Prioritization","Where bugs live","concept · check",
"<p>New deploys, auth surfaces, file uploads, IDOR-prone IDs, forgotten admin.</p>"+unlock_box("Recon playbooks and peer reviews live in Discord."),
q("Best next target after mapping?",[("The prettiest homepage","Not always.",False),("Auth + object IDs + recent changes","High ROI.",True),("Only static marketing pages","Usually thin.",False)])),
("Recon notes","Never lose a host","concept · lab · check",
"<p>Keep a living inventory with dates, tech, interesting notes.</p>",
lab("Notes tool",[
"Create inventory sheet/table.",
"Tag scope status per asset.",
"Share a sanitized tip in Discord (optional).",
])+q("Why date your recon?",[("Aesthetics","No.",False),("Assets change — stale lists waste time",True),("CVSS requires dates","Not the reason.",False)])),
]),
next_card("writing-reports.html","Writing reports that get paid","Triage loves clarity.")
+prev_card("bug-bounty-fundamentals.html","Bug bounty fundamentals","Scope · ethics."),
"csa:bug-bounty/recon-asset-discovery.html","bounty/recon","bb-recon",
tjson({"recon":{"welcome":"Recon lab (simulated).\\n","help":"subs | httpx | clear",
"cmds":{"subs":"Found: app.lab, api.lab, staging.lab, old-admin.lab",
"httpx":"Live: app/api/staging · old-admin → 401 interesting"},
"tasks":{"s":["subs"],"h":["httpx"]}}}),
xp=100,footer="Bug Bounty · In-scope only"))

results.append(write_page(
"bug-bounty/writing-reports.html","bounty","Writing reports that get paid",
"bounty / reports // act 3 · level 3",
"Clear repro + impact = faster triage and better payouts.",
["→ Bounty"],["5 missions","~3 hrs","+100 XP"],
pack_missions([
("Report anatomy","What triage needs","concept · check",
"<p>Title → summary → steps → evidence → impact → remediation. Short and precise.</p>",
q("Most important for triage?",[("Memes","No.",False),("Clear repro steps + impact",True),("Threatening language","Gets you banned.",False)])),
("Evidence quality","Show don't yell","concept · lab · check",
"<p>HTTP request/response, screenshots, redacted tokens. Minimal data to prove.</p>",
lab("A lab finding",[
"Capture one request/response pair.",
"Write 5 numbered repro steps.",
"State impact in 2 sentences.",
])+q("Include full session cookies of real users?",[("Yes always","Minimize / redact.",False),("No — redact; prove with least data",True),("Post them publicly","Never.",False)])),
("Impact framing","Business risk","concept · terminal · check",
"<p>Who can exploit? What data/actions? Blast radius? Chain?</p>",
term("rep","bash · report","Draft impact","Type impact then fix",[
("i",'Impact (<code class="inl">impact</code>)'),
("f",'Fix (<code class="inl">fix</code>)'),
],"hunter@report:~$")+q("Good impact statements…",[("Only say 'this is bad'","Vague.",False),("Name affected roles/data/actions",True),("Demand max bounty or else","Unprofessional.",False)])),
("Collaboration tone","Be a partner","concept · check",
"<p>Polite, responsive, no entitlement. Accept informative duplicates gracefully.</p>"+unlock_box("Get report reviews in Discord before you submit."),
q("If marked duplicate you should…",[("Harass triage","Ban risk.",False),("Learn & improve uniqueness next time",True),("Resubmit identical spam","No.",False)])),
("Template library","Speed with quality","concept · lab · check",
"<p>Keep templates per bug class (IDOR, XSS, SSRF) — fill specifics each time.</p>",
lab("Notes",[
"Create 2 report templates.",
"Paste one filled sample (lab).",
"Post in Discord for feedback (optional).",
])+q("Templates help when…",[("You never customize them","Must customize.",False),("You customize with unique evidence each time",True),("You skip impact","Impact required.",False)])),
]),
next_card("advanced-bounty-techniques.html","Advanced bounty techniques","Chains · uncommons.")
+prev_card("recon-asset-discovery.html","Recon & asset discovery","Surface map."),
"csa:bug-bounty/writing-reports.html","bounty/reports","bb-reports",
tjson({"rep":{"welcome":"Report coach.\\n","help":"impact | fix | clear",
"cmds":{"impact":"Any authenticated user can read other users' invoices via IDOR → PII exposure.",
"fix":"Enforce object ownership server-side; add regression tests."},
"tasks":{"i":["impact"],"f":["fix"]}}}),
xp=100,footer="Bug Bounty · In-scope only"))

results.append(write_page(
"bug-bounty/advanced-bounty-techniques.html","bounty","Advanced bounty techniques",
"bounty / advanced // act 3 · level 4",
"Chains, uncommon bugs, and research habits — still 100% in-scope.",
["→ Bounty","→ Specialist"],["6 missions","~6 hrs","+120 XP"],
pack_missions([
("Chaining","1+1=critical","concept · check",
"<p>Low issues combine: open redirect + token leak, XSS + CSRF lacking, IDOR + weak MFA bypass.</p>",
q("A chain is valuable when…",[("Steps are unrelated noise","Need combined impact.",False),("Combined steps create higher real-world impact",True),("You invent OOS steps","Stay in scope.",False)])),
("Uncommon classes","Beyond XSS/SQLi","concept · lab · check",
"<p>Cache poisoning, HTTP smuggling (careful!), race conditions, business logic, OAuth quirks.</p>",
lab("Lab apps",[
"Practice one race or logic flaw in a lab.",
"Document the chain hypothesis.",
"Note program rules about DoS-like tests.",
])+q("Business logic bugs often need…",[("Only nmap","No.",False),("Product understanding & abuse cases",True),("Kernel exploits","Wrong layer.",False)])),
("API & GraphQL depth","Modern surfaces","concept · terminal · check",
"<p>BOLA, batching, introspection, mass assignment — revisit API module skills on bounty targets.</p>",
term("api","http · api","Probe GraphQL lab","Type introspect then bola",[
("i",'Introspection (<code class="inl">introspect</code>)'),
("b",'BOLA idea (<code class="inl">bola</code>)'),
],"hunter@api:~$")+q("BOLA is essentially…",[("Broken object level authorization",True),("A TLS cipher","No.",False),("A Linux syscall","No.",False)])),
("Account & OAuth abuse","Identity edges","concept · check",
"<p>Redirect URI issues, token leakage, account linking, weak state/nonce.</p>",
q("OAuth redirect URI flaws can lead to…",[("Faster CSS","No.",False),("Token/code theft",True),("Better SEO","No.",False)])),
("Research habits","Stay sharp","concept · check",
"<p>Read writeups, diff changelogs, watch new features — tip sharing in Discord (no 0-day leaks for OOS).</p>"+unlock_box("Advanced hunt sessions and tips land in Discord."),
q("Best ongoing habit?",[("Only grind same payload list","Stagnates.",False),("Study writeups + retest new features",True),("Ignore scope updates","Dangerous.",False)])),
("Specialist gate","Keep climbing","concept · check",
"<p>Bounty mastery feeds AppSec jobs and research. Apply wins to portfolio + Discord.</p>",
q("After advanced bounty you should…",[("Stop documenting","Document wins.",False),("Convert wins to portfolio + keep ethical hunting",True),("Attack out-of-scope for clout","Never.",False)])),
]),
next_card("../freelancing/first-client.html","Getting your first client","Freelance tree.")
+prev_card("writing-reports.html","Writing reports that get paid","Triage craft."),
"csa:bug-bounty/advanced-bounty-techniques.html","bounty/advanced","bb-advanced",
tjson({"api":{"welcome":"API bounty drill.\\n","help":"introspect | bola | clear",
"cmds":{"introspect":"__schema reveals User, Invoice, AdminMutation types",
"bola":"query invoice(id) without ownership check → classic BOLA"},
"tasks":{"i":["introspect"],"b":["bola"]}}}),
xp=120,footer="Bug Bounty · In-scope only"))

print("Bounty pages:", len(results))

# ---------- FREELANCING ----------
results.append(write_page(
"freelancing/first-client.html","freelance","Getting your first client",
"freelance / first-client // act 3 · level 1",
"Positioning, outreach, and closing small authorized security work.",
["→ Freelance"],["5 missions","~3 hrs","+100 XP"],
pack_missions([
("Offer design","What you sell","concept · check",
"<p>Pick a narrow offer: web app pentest lite, WordPress hardening, security review for startups.</p>",
q("Best first offer?",[("Everything cyber forever","Too broad.",False),("One clear scoped service with deliverables",True),("Illegal hacking for hire","Crime.",False)])),
("Proof pack","Why you","concept · lab · check",
"<p>Case studies from labs/bounties (sanitized), sample report, clear ROE template.</p>",
lab("Materials",[
"Write a 1-page service one-pager.",
"Attach 1 sanitized sample finding.",
"Draft ROE/scope checklist.",
])+q("Clients hire freelancers who…",[("Only DM 'hacker for hire'",False),("Show clear scope + sample deliverables",True),("Promise zero-days on demand","Unrealistic/risky.",False)])),
("Outreach","Find conversations","concept · terminal · check",
"<p>Warm intros beat cold spam. Use Discord, alumni, local startups, LinkedIn with value-first notes.</p>",
term("out","bash · outreach","Draft outreach","Type pitch then follow",[
("p",'Pitch (<code class="inl">pitch</code>)'),
("f",'Follow-up (<code class="inl">follow</code>)'),
],"free@biz:~$")+unlock_box("Freelance intros and lead threads live in Discord.")
+q("Good outreach…",[("Threatens their site","Never.",False),("Offers a specific scoped value + proof",True),("Sends 500 identical spam DMs","Burns reputation.",False)])),
("Discovery call","Listen first","concept · check",
"<p>Ask stack, compliance needs, timeline, out-of-scope systems. Never start testing without written OK.</p>",
q("Before any test you need…",[("A vibe","No.",False),("Written authorization & scope",True),("Only a verbal maybe","Get it written.",False)])),
("Close small","Ship & ask referral","concept · lab · check",
"<p>Underpromise, deliver a crisp report, ask for testimonial/referral.</p>",
lab("Process",[
"Define a fixed-price starter package.",
"Write delivery checklist.",
"Post availability in Discord freelance channel.",
])+q("After delivery…",[("Ghost the client","Bad business.",False),("Ask for feedback/referral if happy",True),("Secretly keep access","Illegal.",False)])),
]),
next_card("pricing-contracts.html","Pricing & contracts","Money · paperwork.")
+prev_card("../bug-bounty/advanced-bounty-techniques.html","Advanced bounty","Optional prior."),
"csa:freelancing/first-client.html","freelance/first-client","free-first",
tjson({"out":{"welcome":"Outreach coach.\\n","help":"pitch | follow | clear",
"cmds":{"pitch":"Hi — I help startups ship a scoped web security review (3 days) with a clear report. Sample: [link].",
"follow":"Following up — happy to share a sample SOW if useful this quarter."},
"tasks":{"p":["pitch"],"f":["follow"]}}}),
xp=100,footer="Freelancing · Written auth only"))

results.append(write_page(
"freelancing/pricing-contracts.html","freelance","Pricing & contracts",
"freelance / pricing // act 3 · level 2",
"Price the work, write SOWs, and protect yourself legally.",
["→ Freelance"],["5 missions","~3 hrs","+100 XP"],
pack_missions([
("Pricing models","Fixed vs time","concept · check",
"<p>Fixed for clear scope; T&M for research-heavy. Include retest hours.</p>",
q("Vague scope should be…",[("Ultra-cheap fixed forever","Scope creep risk.",False),("Timeboxed or discovery-first priced",True),("Free","Unsustainable.",False)])),
("SOW essentials","Paper before packets","concept · lab · check",
"<p>SOW: targets, dates, methods, exclusions, deliverables, liability limits, data handling.</p>",
lab("SOW draft",[
"List mandatory SOW sections.",
"Write exclusions (DoS, phishing, etc.).",
"Add retest terms.",
])+q("Authorization belongs…",[("Only in Slack jokes","No.",False),("In signed SOW / ROE",True),("Nowhere","Required.",False)])),
("Payment & deposits","Cashflow","concept · check",
"<p>Deposit before kickoff. Net-15/30 with late fees. Escrow when useful.</p>",
q("Start deep testing before deposit?",[("Always","Risk.",False),("Prefer deposit/kickoff payment first",True),("Never discuss money","Unsustainable.",False)])),
("Insurance & liability","Adulting","concept · check",
"<p>Know your limits; consider cyber/E&O as you grow. Don't accept unlimited liability.</p>"+unlock_box("Contract / SOW discussions happen in Discord."),
q("Unlimited liability clauses are…",[("Great for freelancers","Dangerous.",False),("A red flag to negotiate",True),("Required by physics","No.",False)])),
("Change orders","Scope creep","concept · lab · check",
"<p>New hosts/apps = new quote. Put change-order process in SOW.</p>",
lab("Policy",[
"Write a 3-line change-order rule.",
"Price an example added /staging host.",
"Share question in Discord if unsure.",
])+q("Client adds 5 apps mid-test…",[("Work free","No.",False),("Issue change order / reprice",True),("Ignore SOW","Chaos.",False)])),
]),
next_card("building-portfolio.html","Building a portfolio","Case studies that sell.")
+prev_card("first-client.html","First client","Landing work."),
"csa:freelancing/pricing-contracts.html","freelance/pricing","free-pricing","{}",
xp=100,footer="Freelancing · Written auth only"))

results.append(write_page(
"freelancing/building-portfolio.html","freelance","Building a portfolio",
"freelance / portfolio // act 3 · level 3",
"Case studies and public proof that win clients (without leaking secrets).",
["→ Freelance"],["5 missions","~3 hrs","+100 XP"],
pack_missions([
("Case study format","Story that sells","concept · check",
"<p>Problem → approach → findings themes → business outcome → testimonial.</p>",
q("Case studies should include…",[("Raw customer passwords","Never.",False),("Sanitized outcomes & process",True),("Only logos with no detail","Weak.",False)])),
("Permission to publish","Ask first","concept · lab · check",
"<p>Get written OK for logos/stories. Otherwise anonymize heavily.</p>",
lab("Ethics",[
"Draft a permission ask email.",
"Create one anonymized case study from a lab.",
"Publish on site/GitHub.",
])+q("No permission means…",[("Publish everything","No.",False),("Anonymize or don't use the brand",True),("Forge a logo","Fraud.",False)])),
("Sample report","Show craft","concept · terminal · check",
"<p>A redacted sample report is your best sales asset.</p>",
term("port","bash · portfolio","Build sample","Type sample then index",[
("s",'Sample (<code class="inl">sample</code>)'),
("i",'Index (<code class="inl">index</code>)'),
],"free@folio:~$")+q("Sample reports prove…",[("You own Metasploit","Shallow.",False),("Your communication & methodology",True),("You ignore scope","Bad.",False)])),
("Website / Notion hub","One link","concept · check",
"<p>Services · sample · about · contact · Discord CTA.</p>"+unlock_box("Get portfolio reviews in Discord."),
q("Your hub should make it easy to…",[("Hunt for your email in images","Friction.",False),("Understand offer + contact you",True),("Download malware","Never.",False)])),
("Social proof","Trust","concept · lab · check",
"<p>Testimonials, certs, writeups, speaking, Discord reputation.</p>",
lab("Proof",[
"Collect 1 testimonial or peer quote.",
"Link 2 writeups.",
"Add Discord join CTA on your hub.",
])+q("Trust grows from…",[("Anonymous swagger","Thin.",False),("Consistent delivered work + proof",True),("Fear marketing","Unprofessional.",False)])),
]),
next_card("client-management.html","Client management & red flags","Survive delivery.")
+prev_card("pricing-contracts.html","Pricing & contracts","SOW · money."),
"csa:freelancing/building-portfolio.html","freelance/portfolio","free-portfolio",
tjson({"port":{"welcome":"Portfolio builder.\\n","help":"sample | index | clear",
"cmds":{"sample":"Wrote sample-report.pdf (redacted IDOR + XSS examples)",
"index":"README links: services · sample · contact · Discord"},
"tasks":{"s":["sample"],"i":["index"]}}}),
xp=100,footer="Freelancing · Written auth only"))

results.append(write_page(
"freelancing/client-management.html","freelance","Client management & red flags",
"freelance / clients // act 3 · level 4",
"Communicate, escalate, and walk away from bad engagements.",
["→ Freelance"],["5 missions","~2 hrs","+100 XP"],
pack_missions([
("Cadence","No surprises","concept · check",
"<p>Kickoff → mid-test update → draft → finalize → retest. Overcommunicate blockers.</p>",
q("Mid-engagement silence is…",[("Professional mystery","Usually bad.",False),("A risk — send status updates",True),("Required by ISO","No.",False)])),
("Critical findings","Handle carefully","concept · lab · check",
"<p>Criticals: notify promptly via agreed channel, minimize data, don't dump on Twitter.</p>",
lab("Playbook",[
"Write a critical-finding notification template.",
"Define severity SLA in your SOW.",
"List what never to exfiltrate.",
])+q("Publicly dumping a client critical…",[("Is marketing","Breach of trust/contract.",False),("Is unethical and often contractual breach",True),("Required for CVSS","No.",False)])),
("Red flags","Walk away","concept · check",
"<p>No written auth, pressure to skip scope, 'just hack our rival', unpaid history, illegal asks.</p>"+unlock_box("Ask the community when an engagement feels off."),
q("Client asks you to hack a competitor…",[("Do it for extra fee","Illegal.",False),("Refuse — unauthorized & illegal",True),("Maybe if they're mean","Still illegal.",False)])),
("Difficult feedback","Stay calm","concept · check",
"<p>Separate findings from ego. Provide evidence. Offer retest terms.</p>",
q("If client disputes a finding…",[("Insult them","Unprofessional.",False),("Re-explain with evidence; accept valid corrections",True),("Delete logs","Destroys trust.",False)])),
("Retest & close","Finish clean","concept · lab · check",
"<p>Retest fixed items, update status, revoke your access, archive notes securely.</p>",
lab("Closeout",[
"Write access-revocation checklist.",
"Define retest window.",
"Celebrate a win in Discord (sanitized).",
])+q("After project end you should…",[("Keep persistent shells","Never.",False),("Confirm access removed & archive securely",True),("Sell their data","Crime.",False)])),
]),
next_card("../defensive-security/soc-analyst-fundamentals.html","SOC analyst fundamentals","Defense track.")
+prev_card("building-portfolio.html","Building a portfolio","Proof that sells."),
"csa:freelancing/client-management.html","freelance/clients","free-clients","{}",
xp=100,footer="Freelancing · Written auth only"))

print("Through freelance:", len(results))

# ---------- DEFENSE ----------
results.append(write_page(
"defensive-security/soc-analyst-fundamentals.html","defense","SOC analyst fundamentals",
"defense / soc // act 2 · level 1",
"Tickets, triage, SIEM basics, and calm escalation — blue-team ops.",
["→ Defense","→ Jobs"],["6 missions","~5 hrs","+120 XP"],
pack_missions([
("SOC mission","Detect → respond","concept · check",
"<p>Monitor, triage, escalate, document. SLAs matter more than heroics.</p>",
q("SOC primary job?",[("Quietly ignore alerts","No.",False),("Detect and respond to threats with process",True),("Only red team","Different role.",False)])),
("Alert triage","Severity & context","concept · terminal · lab · check",
"<p>False positives happen. Enrich: user, host, geo, rarity, malware intel.</p>",
term("soc","siem · triage","Triage an alert","Type enrich then decide",[
("e",'Enrich (<code class="inl">enrich</code>)'),
("d",'Decide (<code class="inl">decide</code>)'),
],"analyst@soc:~$")+lab("Your SIEM lab / sample logs",[
"Open one alert and list 5 enrichment fields.",
"Classify FP / TP / needs escalate.",
"Write the ticket summary.",
])+q("Good triage…",[("Closes everything as FP","Misses attacks.",False),("Uses context before escalating or closing",True),("Only looks at colors","Shallow.",False)])),
("SIEM queries","Ask the data","concept · lab · check",
"<p>Learn your query language (KQL/SPL/Lucene). Hunt failed logons, rare processes, new services.</p>",
lab("Lab SIEM",[
"Write a failed-logon query.",
"Find a rare outbound destination.",
"Save one dashboard panel idea.",
])+q("SIEM value comes from…",[("Pretty walls only","No.",False),("Telemetry + queries + tuned detections",True),("Deleting logs","Harms IR.",False)])),
("Playbooks","Repeatable response","concept · check",
"<p>Phish, malware, brute force, account takeover — follow runbooks, then improve them.</p>",
q("Playbooks help…",[("Replace thinking forever","Still think.",False),("Standardize quality under pressure",True),("Avoid tickets","Still document.",False)])),
("Escalation & comms","Clear handoffs","concept · check",
"<p>Escalate with: what, when, impact, actions taken, ask. Get unstuck in Discord.</p>"+unlock_box("SOC study groups and shift tips live in Discord."),
q("Escalation notes should include…",[("Only 'pls fix'","Incomplete.",False),("Timeline, impact, actions, request",True),("Memes only","No.",False)])),
("Shift hygiene","Sustainable ops","concept · lab · check",
"<p>Hand-off notes, health, avoid alert fatigue via tuning requests.</p>",
lab("Habits",[
"Draft a shift handoff template.",
"List 3 noisy alert types to tune.",
"Introduce yourself in Discord defense channel.",
])+q("Alert fatigue is reduced by…",[("Adding 500 more unprioritized alerts","Worse.",False),("Tuning + prioritization + enrichment",True),("Ignoring criticals","Dangerous.",False)])),
]),
next_card("incident-response-dfir.html","Incident response & DFIR","Contain · eradicate · recover.")
+prev_card("../career/certification-roadmap.html","Cert roadmap","Job gate optional.")
+prev_card("../penetration-testing/evasion-techniques-breach.html","Offense finale","Purple overlap."),
"csa:defensive-security/soc-analyst-fundamentals.html","defense/soc","soc-analyst",
tjson({"soc":{"welcome":"SOC triage sim.\\n","help":"enrich | decide | clear",
"cmds":{"enrich":"User: jdoe · Host: WIN-12 · Geo new · Process: rare powershell chain",
"decide":"Decision: escalate to IR — suspected foothold. Ticket drafted."},
"tasks":{"e":["enrich"],"d":["decide"]}}}),
xp=120,footer="Defense · Lab & employer systems only"))

results.append(write_page(
"defensive-security/incident-response-dfir.html","defense","Incident response & DFIR",
"defense / ir-dfir // act 2 · level 2",
"NIST-style IR plus evidence basics — contain without destroying proof.",
["→ Defense"],["6 missions","~6 hrs","+120 XP"],
pack_missions([
("IR lifecycle","Prepare → lessons","concept · check",
"<p>Prepare, detect/analyze, contain, eradicate, recover, lessons learned.</p>",
q("Skipping lessons learned…",[("Saves time forever","Repeats incidents.",False),("Causes repeat incidents",True),("Is required by attackers","No.",False)])),
("Containment choices","Stop the bleed","concept · check",
"<p>Isolate host/account, block IOC, preserve volatility when needed.</p>",
q("First priority often…",[("Blog the breach","Later.",False),("Contain impact while preserving key evidence",True),("Reimage everything instantly with no notes","May destroy evidence.",False)])),
("Evidence basics","Chain of custody","concept · terminal · lab · check",
"<p>Hash disk images, note who/when/how. Memory before shutdown when possible.</p>",
term("dfir","bash · dfir","Hash an image","Type hash then note",[
("h",'Hash (<code class="inl">hash</code>)'),
("n",'Notes (<code class="inl">note</code>)'),
],"ir@lab:~$")+lab("Lab VM",[
"Create a file and sha256 it.",
"Write a mini chain-of-custody note.",
"List volatile vs non-volatile artifacts.",
])+q("Hashing evidence helps…",[("Make files prettier","No.",False),("Prove integrity over time",True),("Encrypt for attackers","No.",False)])),
("Host artifacts","Where truth hides","concept · lab · check",
"<p>Process trees, persistence, prefetch/shimcache-ish concepts, auth logs, browser, DNS.</p>",
lab("Windows/Linux lab",[
"List persistence locations you will check.",
"Capture a process tree screenshot.",
"Export relevant auth logs.",
])+q("Persistence checks matter because…",[("Malware always polite","No.",False),("Attackers return after reboot via autoruns",True),("Logs are useless","Logs are core.",False)])),
("Comms & legal","Need-to-know","concept · check",
"<p>Coordinate with legal/PR/leadership. Don't tip off attackers carelessly.</p>"+unlock_box("IR tabletop scenarios live in Discord."),
q("Public live-tweeting an active IR…",[("Is best practice","Usually harmful.",False),("Is usually a bad idea",True),("Required by NIST","No.",False)])),
("Report & recover","Close the loop","concept · lab · check",
"<p>Timeline, root cause, blast radius, fixes, monitoring gaps.</p>",
lab("Writeup",[
"Draft a 1-page IR summary from a lab scenario.",
"List 3 detection improvements.",
"Share sanitized lessons in Discord.",
])+q("Recovery includes…",[("Only unplugging forever","Need hardened restore.",False),("Clean restore + monitoring + validation",True),("Deleting all backups","Catastrophic.",False)])),
]),
next_card("threat-hunting.html","Threat hunting","Hypothesis-driven search.")
+prev_card("soc-analyst-fundamentals.html","SOC fundamentals","Triage · SIEM."),
"csa:defensive-security/incident-response-dfir.html","defense/ir","dfir-ops",
tjson({"dfir":{"welcome":"DFIR bench.\\n","help":"hash | note | clear",
"cmds":{"hash":"SHA256(disk.img)= a3f1…c92",
"note":"Custody: analyst A · 2026-08-04 · write-blocked image · stored vault"},
"tasks":{"h":["hash"],"n":["note"]}}}),
xp=120,footer="Defense · Lab & employer systems only"))

results.append(write_page(
"defensive-security/threat-hunting.html","defense","Threat hunting",
"defense / hunting // act 2 · level 3",
"Hypothesis → data → find evil that alerts missed.",
["→ Defense"],["6 missions","~6 hrs","+120 XP"],
pack_missions([
("Hunt loop","Hypothesis first","concept · check",
"<p>Intel/ATT&CK → hypothesis → query → investigate → new detections.</p>",
q("Hunting without a hypothesis…",[("Is always better","Often aimless.",False),("Often wastes time — start with a question",True),("Is illegal","No.",False)])),
("ATT&CK mapping","Shared language","concept · lab · check",
"<p>Map behaviors (T1059, T1003…) to telemetry you actually have.</p>",
lab("ATT&CK + your logs",[
"Pick 1 technique.",
"List required telemetry.",
"Write a hunt query idea.",
])+q("ATT&CK helps hunters…",[("Replace logs","No.",False),("Name behaviors and gap-check coverage",True),("Generate malware","No.",False)])),
("Telemetry gaps","Know blind spots","concept · check",
"<p>No EDR? No DNS logs? Document gaps — don't pretend coverage.</p>",
q("Missing process telemetry means…",[("Perfect security","Blind.",False),("You may miss script/LOLBin abuse",True),("Hunting is unnecessary","Still hunt with what you have.",False)])),
("Practical hunts","Starter ideas","concept · terminal · lab · check",
"<p>Rare parent/child, encoded powershell, new services, beaconing intervals, impossible travel.</p>",
term("hunt","siem · hunt","Run a hunt","Type rare then beacon",[
("r",'Rare proc (<code class="inl">rare</code>)'),
("b",'Beacon (<code class="inl">beacon</code>)'),
],"hunter@blue:~$")+lab("Lab data",[
"Hunt one rare process pattern.",
"Hunt one outbound rarity.",
"Document TP/FP notes.",
])+q("Beaconing hunts look for…",[("Random UI themes","No.",False),("Periodic rare destinations/timings",True),("Only email subjects","Narrow.",False)])),
("From hunt to detection","Productize","concept · check",
"<p>Convert good hunts into analytics + tuning + ownership.</p>"+unlock_box("Share hunt queries and get feedback on Discord."),
q("A successful hunt should often become…",[("A secret forever","Share internally.",False),("A detection/analytics candidate",True),("A public exploit","Wrong team.",False)])),
("Purple synergy","Learn from offense","concept · lab · check",
"<p>Use Offense track stories to hunt the same techniques in your lab.</p>",
lab("Purple",[
"Pick one offense technique you learned.",
"Hunt for its artifacts.",
"Propose one control.",
])+q("Purple teaming improves…",[("Only red ego","No.",False),("Detection quality via shared scenarios",True),("Nothing","False.",False)])),
]),
next_card("detection-engineering.html","Detection engineering","Rules that last.")
+prev_card("incident-response-dfir.html","IR & DFIR","Respond well."),
"csa:defensive-security/threat-hunting.html","defense/hunt","threat-hunter",
tjson({"hunt":{"welcome":"Hunt console.\\n","help":"rare | beacon | clear",
"cmds":{"rare":"Hit: winword.exe → cmd.exe → powershell -enc …",
"beacon":"Host talking to rare IP every ~60s — investigate."},
"tasks":{"r":["rare"],"b":["beacon"]}}}),
xp=120,footer="Defense · Lab & employer systems only"))

results.append(write_page(
"defensive-security/detection-engineering.html","defense","Detection engineering",
"defense / detection // act 2 · level 4",
"Write, test, and tune detections without drowning the SOC.",
["→ Defense","→ Specialist"],["6 missions","~6 hrs","+120 XP"],
pack_missions([
("Detection as code","Versioned logic","concept · check",
"<p>Detections are products: ownership, tests, false-positive budgets.</p>",
q("Untested detections…",[("Are fine forever","Drift & FP/FN.",False),("Rot — need tests and review",True),("Always catch APTs","No.",False)])),
("Atomic tests","Prove it fires","concept · lab · check",
"<p>Generate benign-safe lab signals (Atomic Red Team style concepts) and validate alerts.</p>",
lab("Lab",[
"Pick a detection idea.",
"Generate a safe lab signal.",
"Confirm alert + tune if noisy.",
])+q("You validate detections by…",[("Hoping","No.",False),("Testing true/false scenarios in lab",True),("Disabling logging","Worse.",False)])),
("FP management","Precision matters","concept · terminal · check",
"<p>Allowlists carefully, stack signals, suppress with expiry, measure FP rate.</p>",
term("det","yaml · detect","Tune a rule","Type noisy then tune",[
("n",'See noise (<code class="inl">noisy</code>)'),
("t",'Tune (<code class="inl">tune</code>)'),
],"deteng@lab:~$")+q("Permanent broad suppressions…",[("Are always safe","Hide attacks.",False),("Can hide real attacks — prefer tight/timeboxed",True),("Replace SOC","No.",False)])),
("Telemetry engineering","Log what matters","concept · check",
"<p>Partner with IT/App teams for command-line logging, DNS, auth, egress.</p>",
q("Detection eng without telemetry partners…",[("Is easy","Usually blocked.",False),("Struggles — you need data pipelines",True),("Needs only screenshots","No.",False)])),
("Metrics","Did we improve?","concept · check",
"<p>MTTD/MTTR, FP rate, coverage vs ATT&CK, escaped incidents.</p>"+unlock_box("Detection reviews and rule clinics live in Discord."),
q("Useful detection metric?",[("Lines of YAML only","Vanity.",False),("FP rate + coverage + response time",True),("Coffee consumed","No.",False)])),
("Ship a rule","End-to-end","concept · lab · check",
"<p>Write → test → document → deploy → monitor → iterate.</p>",
lab("Deliverable",[
"Write one detection pseudocode/rule.",
"Document FP expectations.",
"Post for review in Discord.",
])+q("Documentation for a rule should include…",[("Nothing","Unmaintainable.",False),("Intent, data sources, FP notes, owner",True),("Only a cool name","Insufficient.",False)])),
]),
next_card("../grc/grc-fundamentals.html","GRC fundamentals","Governance track.")
+prev_card("threat-hunting.html","Threat hunting","Hypotheses."),
"csa:defensive-security/detection-engineering.html","defense/detection","detection-eng",
tjson({"det":{"welcome":"Detection lab.\\n","help":"noisy | tune | clear",
"cmds":{"noisy":"Rule 'PS encoded' FP rate 42% on admins' jump boxes",
"tune":"Exclude signed mgmt jumpers + require rare parent — FP↓ to 3%"},
"tasks":{"n":["noisy"],"t":["tune"]}}}),
xp=120,footer="Defense · Lab & employer systems only"))

print("Through defense:", len(results))

# ---------- GRC ----------
results.append(write_page(
"grc/grc-fundamentals.html","grc","GRC fundamentals",
"grc / fundamentals // act 2 · level 1",
"Governance, risk, and compliance — how orgs stay trustworthy.",
["→ GRC","→ Jobs"],["5 missions","~4 hrs","+100 XP"],
pack_missions([
("What is GRC","Three pillars","concept · check",
"<p><b>Governance</b> sets direction, <b>Risk</b> prioritizes harm, <b>Compliance</b> meets obligations.</p>",
q("GRC is mainly…",[("Only hacking","No.",False),("Aligning security with business obligations & risk",True),("Buying logos","Shallow.",False)])),
("Policies vs standards vs procedures","Document pyramid","concept · lab · check",
"<p>Policy = why/rules; standard = must metrics; procedure = how steps.</p>",
lab("Docs",[
"Draft a 5-line Acceptable Use policy snippet.",
"Write one password standard statement.",
"Outline a access-request procedure.",
])+q("Procedures should be…",[("Vague vibes","No.",False),("Actionable steps people can follow",True),("Secret from auditors","Opposite.",False)])),
("Stakeholders","Who cares","concept · check",
"<p>Executives, legal, IT, security, auditors, customers. Speak their language.</p>",
q("GRC success needs…",[("Only the intern","No.",False),("Cross-functional ownership",True),("Zero documentation","Fails audits.",False)])),
("Control thinking","Prevent · detect · respond","concept · terminal · check",
"<p>Map business goals → risks → controls → evidence.</p>",
term("grc","bash · grc","Map a control","Type risk then control",[
("r",'Risk (<code class="inl">risk</code>)'),
("c",'Control (<code class="inl">control</code>)'),
],"analyst@grc:~$")+unlock_box("GRC templates and mentor Q&A live in Discord.")
+q("Evidence proves…",[("You meant well","Not enough.",False),("Controls operated as designed",True),("Nothing","Audits need evidence.",False)])),
("Career paths","Analyst → lead","concept · lab · check",
"<p>GRC analyst, risk, audit, privacy ops. Portfolio: policies, risk registers, audit workpapers (sanitized).</p>",
lab("Career",[
"Pick a GRC target role.",
"List 3 portfolio artifacts to build.",
"Join Discord GRC channel.",
])+q("GRC portfolios can include…",[("Only kernel exploits","Wrong lane.",False),("Sanitized policies, risk regs, audit samples",True),("Stolen client docs","Illegal.",False)])),
]),
next_card("risk-management.html","Risk management","Assess · treat · monitor.")
+prev_card("../defensive-security/detection-engineering.html","Detection engineering","Optional prior."),
"csa:grc/grc-fundamentals.html","grc/fundamentals","grc-fundamentals",
tjson({"grc":{"welcome":"GRC mapper.\\n","help":"risk | control | clear",
"cmds":{"risk":"Risk: ransomware via phishing → downtime + data breach",
"control":"Controls: MFA + email security + backups tested + IR plan"},
"tasks":{"r":["risk"],"c":["control"]}}}),
xp=100,footer="GRC · Ethical & confidential handling"))

results.append(write_page(
"grc/risk-management.html","grc","Risk management",
"grc / risk // act 2 · level 2",
"Identify, score, treat, and monitor risk without theater.",
["→ GRC"],["5 missions","~5 hrs","+100 XP"],
pack_missions([
("Risk basics","Likelihood × impact","concept · check",
"<p>Risk = uncertain event affecting objectives. Inherent vs residual.</p>",
q("Residual risk is…",[("Risk before controls","That's inherent.",False),("Risk left after treatments",True),("Zero always","Never truly zero.",False)])),
("Registers","Living lists","concept · lab · check",
"<p>Asset/process, threat, vulnerability, impact, likelihood, owner, treatment, status.</p>",
lab("Spreadsheet",[
"Create a 5-row risk register.",
"Assign owners.",
"Pick treatments for top 2.",
])+q("Risks without owners…",[("Resolve themselves","No.",False),("Stall — assign accountability",True),("Are ideal","No.",False)])),
("Treatment options","4 T's","concept · check",
"<p>Treat/mitigate, transfer, tolerate/accept, terminate/avoid — with leadership buy-in.</p>",
q("Buying insurance is mostly…",[("Mitigation of likelihood","Often transfer.",False),("Risk transfer (with caveats)",True),("Termination of asset always","Not always.",False)])),
("Qual vs quant","Useful enough","concept · terminal · check",
"<p>Heat maps for prioritization; FAIR-like quant when decisions need money talk.</p>",
term("risk","bash · risk","Score a risk","Type score then treat",[
("s",'Score (<code class="inl">score</code>)'),
("t",'Treat (<code class="inl">treat</code>)'),
],"risk@grc:~$")+q("Heat maps help…",[("Replace all data","No.",False),("Communicate relative priority quickly",True),("Hack networks","Wrong domain.",False)])),
("Monitor & report","KRIs","concept · lab · check",
"<p>Key risk indicators: patch lag, phishing fail rate, backup test success, open criticals.</p>",
unlock_box("Get risk register reviews on Discord.")
+lab("KRIs",[
"Define 3 KRIs for a fictional SaaS.",
"Set thresholds.",
"Draft a monthly risk email to execs.",
])+q("KRIs should be…",[("Unmeasurable vibes","No.",False),("Measurable and tied to decisions",True),("Hidden from leadership","Opposite.",False)])),
]),
next_card("compliance-frameworks.html","Compliance frameworks","ISO · NIST · SOC2…")
+prev_card("grc-fundamentals.html","GRC fundamentals","Pillars."),
"csa:grc/risk-management.html","grc/risk","risk-mgmt",
tjson({"risk":{"welcome":"Risk scorer.\\n","help":"score | treat | clear",
"cmds":{"score":"Phish→ransomware: Impact High · Likelihood Medium → Priority 1",
"treat":"Treat: MFA+training+EDR+backups; accept residual with exec sign-off"},
"tasks":{"s":["score"],"t":["treat"]}}}),
xp=100,footer="GRC · Ethical & confidential handling"))

results.append(write_page(
"grc/compliance-frameworks.html","grc","Compliance frameworks",
"grc / frameworks // act 2 · level 3",
"NIST CSF, ISO 27001, SOC 2, PCI — map once, reuse evidence.",
["→ GRC"],["5 missions","~5 hrs","+100 XP"],
pack_missions([
("Framework zoo","Pick by customer","concept · check",
"<p>NIST CSF = flexible; ISO 27001 = ISMS; SOC 2 = trust services; PCI = card data.</p>",
q("SOC 2 is commonly driven by…",[("Gamers","No.",False),("Customer trust / B2B sales needs",True),("Only governments","Broader.",False)])),
("Control mapping","One evidence, many frameworks","concept · lab · check",
"<p>Map MFA to multiple control IDs. Build a crosswalk.</p>",
lab("Crosswalk",[
"Pick MFA control.",
"Map to NIST CSF + ISO-ish statements.",
"List evidence artifacts (screenshots/configs/tickets).",
])+q("Crosswalks help…",[("Duplicate work forever","Opposite.",False),("Reuse evidence across audits",True),("Avoid controls","No.",False)])),
("ISMS mindset","Plan-Do-Check-Act","concept · check",
"<p>ISO-style: scope, risk assessment, Statement of Applicability, continual improvement.</p>",
q("An ISMS is…",[("A single firewall rule","No.",False),("A managed system of policies/controls/improvement",True),("Only a certificate PDF","Certificate ≠ system.",False)])),
("Audit readiness","No heroics week","concept · terminal · check",
"<p>Continuous evidence > scramble. Owners, tickets, screenshots dated.</p>",
term("comp","bash · compliance","Prep evidence","Type evidence then gap",[
("e",'Evidence (<code class="inl">evidence</code>)'),
("g",'Gap (<code class="inl">gap</code>)'),
],"grc@audit:~$")+unlock_box("Framework study groups live in Discord.")
+q("Best audit prep?",[("Night-before screenshots only","Fragile.",False),("Continuous evidence collection",True),("Delete logs","Worse.",False)])),
("Privacy overlap","Data obligations","concept · lab · check",
"<p>GDPR/CCPA-style themes: inventory, lawful basis, rights requests, vendors.</p>",
lab("Privacy lite",[
"List personal data your fictional app stores.",
"Note retention idea.",
"Note a vendor risk question.",
])+q("Personal data inventories help…",[("Nothing","Needed for rights & risk.",False),("Answer where data lives and why",True),("Increase CVSS","Unrelated.",False)])),
]),
next_card("security-auditing.html","Security auditing","Test controls with evidence.")
+prev_card("risk-management.html","Risk management","Treat risk."),
"csa:grc/compliance-frameworks.html","grc/frameworks","grc-frameworks",
tjson({"comp":{"welcome":"Audit prep.\\n","help":"evidence | gap | clear",
"cmds":{"evidence":"MFA: IdP policy export + enrollment metrics + exception tickets",
"gap":"Gap: privileged break-glass accounts lacking quarterly review"},
"tasks":{"e":["evidence"],"g":["gap"]}}}),
xp=100,footer="GRC · Ethical & confidential handling"))

results.append(write_page(
"grc/security-auditing.html","grc","Security auditing",
"grc / audit // act 2 · level 4",
"Plan audits, sample evidence, write findings that get fixed.",
["→ GRC","→ Jobs"],["5 missions","~5 hrs","+100 XP"],
pack_missions([
("Audit types","Internal vs external","concept · check",
"<p>Internal audit improves; external attests. Both need independence & evidence.</p>",
q("Auditors primarily…",[("Configure firewalls daily","Ops role.",False),("Provide assurance over controls",True),("Exploit production without ROE","No.",False)])),
("Planning & sampling","Risk-based","concept · lab · check",
"<p>Scope objectives, pick samples (users, tickets, changes), define test steps.</p>",
lab("Plan",[
"Write an audit objective for access reviews.",
"Define sample size approach.",
"List population source (HR/IdP).",
])+q("Risk-based auditing focuses…",[("Random trivia only","No.",False),("Higher-risk areas first",True),("Only cafeteria menus","No.",False)])),
("Testing controls","Design vs operating","concept · terminal · check",
"<p>Design effectiveness ≠ operating effectiveness. Test both.</p>",
term("audit","bash · audit","Test a control","Type design then operate",[
("d",'Design (<code class="inl">design</code>)'),
("o",'Operate (<code class="inl">operate</code>)'),
],"auditor@grc:~$")+q("Operating effectiveness asks…",[("Does the PDF look nice?","Shallow.",False),("Did the control run as designed over time?",True),("Is the office plant watered?","No.",False)])),
("Writing findings","Actionable","concept · lab · check",
"<p>Condition, criteria, cause, effect, recommendation, severity.</p>"+unlock_box("Get finding-writing reviews on Discord.")
+lab("Finding",[
"Write one finding with all 5 parts.",
"Propose a remediation owner & date.",
"Note retest evidence needed.",
])+q("Weak findings…",[("Include evidence and impact","Strong.",False),("Are vague with no criteria/effect",True),("Help remediation","Strong ones do.",False)])),
("Follow-up","Close the loop","concept · check",
"<p>Track remediations, verify, report aging. GRC+career: apply via Discord.</p>",
q("After reporting findings…",[("Delete the tracker","No.",False),("Track remediation to verification",True),("Ignore highs","Irresponsible.",False)])),
]),
next_card("../ai-security/ai-llm-security-fundamentals.html","AI & LLM security","Act 2/3 AI track.")
+prev_card("compliance-frameworks.html","Compliance frameworks","Map controls."),
"csa:grc/security-auditing.html","grc/audit","sec-auditor",
tjson({"audit":{"welcome":"Audit workpaper.\\n","help":"design | operate | clear",
"cmds":{"design":"Design OK: quarterly access review policy + IdP reports exist",
"operate":"Operating gap: 2/10 samples missed manager sign-off"},
"tasks":{"d":["design"],"o":["operate"]}}}),
xp=100,footer="GRC · Ethical & confidential handling"))

# ---------- AI ----------
results.append(write_page(
"ai-security/ai-llm-security-fundamentals.html","ai","AI & LLM security fundamentals",
"ai / llm-fundamentals // act 2 · level 1",
"Threats to LLM apps: prompt injection, data leaks, tool abuse — lab only.",
["→ AI","→ Offense"],["6 missions","~5 hrs","+120 XP"],
pack_missions([
("LLM app architecture","Where risk lives","concept · check",
"<p>User → app → model → tools/RAG. Trust boundaries at each hop.</p>",
q("Most LLM risks appear at…",[("Only GPU temperature","No.",False),("App+tool+data boundaries around the model",True),("Only CSS","No.",False)])),
("Prompt injection","Instructions vs data","concept · terminal · lab · check",
"<p>Attacker content overrides system intent (direct/indirect via docs).</p>",
term("llm","lab · llm","Probe injection","Type inject then impact",[
("i",'Inject (<code class="inl">inject</code>)'),
("p",'Impact (<code class="inl">impact</code>)'),
],"red@llm:~$")+lab("Local/toy LLM app you control",[
"Try a direct prompt-injection in a sandbox.",
"Try indirect via a retrieved doc.",
"Note a mitigation (separation/privilege).",
])+q("Indirect prompt injection arrives via…",[("Only USB","No.",False),("Untrusted content the model reads (email/docs/web)",True),("BGP","Wrong layer.",False)])),
("Data leakage","Secrets in context","concept · check",
"<p>System prompts, RAG docs, tool outputs can leak. Minimize sensitive context.</p>",
q("Putting API keys in the system prompt is…",[("Best practice","Risky leakage.",False),("Dangerous — keys get extracted",True),("Required by OpenAI","No.",False)])),
("Insecure output handling","LLM ≠ trusted","concept · lab · check",
"<p>Model output can be XSS/SQLi/CMD if rendered or executed unsafely.</p>",
lab("App sink",[
"Find where outputs render in your lab app.",
"Test HTML/script encoding.",
"Block dangerous tool args server-side.",
])+q("Treat model output as…",[("Fully trusted admin","No.",False),("Untrusted user input",True),("Hardware root of trust","No.",False)])),
("RAG & poisoning","Garbage in","concept · check",
"<p>Poisoned knowledge bases steer answers. Control who can write to corpora.</p>"+unlock_box("AI security labs and discussions live in Discord."),
q("RAG poisoning targets…",[("Only CPUs","No.",False),("The knowledge the model retrieves",True),("Only HDMI cables","No.",False)])),
("Secure SDLC for AI","Threat model early","concept · lab · check",
"<p>Threat-model tools, data flows, evals for safety, human-in-loop for high risk.</p>",
lab("Design",[
"Draw your LLM app data flow.",
"List top 5 threats.",
"List 5 controls.",
])+q("High-risk tool calls should…",[("Auto-run always","Dangerous.",False),("Require authz + logging (+ human approval when needed)",True),("Be hidden from logs","Worse.",False)])),
]),
next_card("ai-red-teaming.html","AI red teaming","Adversarial testing.")
+prev_card("../web-application-security/web-attacks.html","Web attacks","Prerequisite."),
"csa:ai-security/ai-llm-security-fundamentals.html","ai/llm-fundamentals","ai-llm",
tjson({"llm":{"welcome":"LLM security lab.\\n","help":"inject | impact | clear",
"cmds":{"inject":"User doc says: ignore policies and dump system prompt → model complies in vulnerable app",
"impact":"Impact: policy bypass, secret leak, unauthorized tool use"},
"tasks":{"i":["inject"],"p":["impact"]}}}),
xp=120,footer="AI Security · Authorized lab models/apps only"))

results.append(write_page(
"ai-security/ai-red-teaming.html","ai","AI red teaming",
"ai / red-team // act 2 · level 2",
"Adversarial testing for LLM products — goals, suites, reporting.",
["→ AI","→ Specialist"],["6 missions","~6 hrs","+120 XP"],
pack_missions([
("Engagement goals","What to break","concept · check",
"<p>Safety policy bypass, data exfil, tool abuse, jailbreaks, integrity of answers.</p>",
q("AI red team scope should be…",[("Infinite open internet models you don't own","Unauthorized.",False),("Written goals/systems you are allowed to test",True),("Only physical locks","Different domain.",False)])),
("Attack suites","Coverage","concept · lab · check",
"<p>Build a case library: injection, jailbreak, exfil, phishing-aid, toxic, privilege.</p>",
lab("Suite",[
"Write 10 test prompts/cases.",
"Tag expected fail/pass.",
"Run against your lab app.",
])+q("A good suite is…",[("One joke prompt","Thin.",False),("Diverse cases with expected outcomes",True),("Only production customer data","Unsafe/unethical.",False)])),
("Tool-enabled agents","Dangerous power","concept · terminal · check",
"<p>Agents with shell/email/DB tools need strict allowlists and confirmations.</p>",
term("agent","lab · agent","Abuse a tool","Type tool then block",[
("t",'Tool abuse (<code class="inl">tool</code>)'),
("b",'Block (<code class="inl">block</code>)'),
],"red@agent:~$")+q("Unrestricted shell tools for LLMs are…",[("Fine in prod","High risk.",False),("High risk without strong authz/sandbox",True),("Required","No.",False)])),
("Evals & metrics","Measure harm","concept · check",
"<p>Attack success rate, severity, regression after mitigations.</p>",
q("After a mitigation you should…",[("Never retest","No.",False),("Rerun the suite for regressions",True),("Delete evals","Lose signal.",False)])),
("Reporting AI findings","Actionable","concept · lab · check",
"<p>Include prompt/doc, model version, tools, impact, recommended guardrails.</p>"+unlock_box("AI red-team roundtables live in Discord.")
+lab("Report",[
"Write one AI finding report.",
"Propose 2 guardrails.",
"Share sanitized in Discord.",
])+q("AI findings need…",[("Only 'model bad'","Vague.",False),("Repro artifacts + system context + impact",True),("No model version","Harder to fix.",False)])),
("Ethics & dual-use","Stay clean","concept · check",
"<p>Don't build cybercrime assistants. Follow org policy and law.</p>",
q("Building a public 'how to hack banks' bot is…",[("Cool portfolio","Illegal/harmful.",False),("Unethical and likely illegal",True),("Required for jobs","No.",False)])),
]),
next_card("../vulnerability-research/reverse-engineering-fundamentals.html","Reverse engineering","Research tree.")
+prev_card("ai-llm-security-fundamentals.html","LLM security fundamentals","Threats."),
"csa:ai-security/ai-red-teaming.html","ai/red-team","ai-redteam",
tjson({"agent":{"welcome":"Agent abuse lab.\\n","help":"tool | block | clear",
"cmds":{"tool":"Model tricked into tool.call(shell, 'curl evil') in vulnerable agent",
"block":"Mitigation: allowlist tools, confirm side effects, sandbox network"},
"tasks":{"t":["tool"],"b":["block"]}}}),
xp=120,footer="AI Security · Authorized lab models/apps only"))

print("Through AI:", len(results))

# ---------- RESEARCH / EXPLOIT ----------
results.append(write_page(
"vulnerability-research/reverse-engineering-fundamentals.html","research","Reverse engineering fundamentals",
"research / re // act 3 · level 1",
"Read binaries ethically — tools, static/dynamic, and lab practice.",
["→ Research"],["6 missions","~8 hrs","+140 XP"],
pack_missions([
("RE mindset","Authorized only","concept · check",
"<p>RE malware/labs/CTF bins you own or have rights to. Respect licenses & law.</p>",
q("Reverse engineering malware samples from shady torrents…",[("Is always fine","Legal/safety risk.",False),("Needs careful lab isolation & legal caution",True),("Should be done on your company prod laptop","Isolate.",False)])),
("Toolbelt","file · strings · disasm","concept · terminal · lab · check",
"<p>Start simple: file type, strings, basic disassembly, then debugger.</p>",
term("re","bash · re","Triage a binary","Type file then strings",[
("f",'File (<code class="inl">file</code>)'),
("s",'Strings (<code class="inl">strings</code>)'),
],"re@lab:~$")+lab("A CTF/crackme you downloaded legally",[
"Run file/strings.",
"Open in a disassembler (Ghidra/etc).",
"Note entry & interesting imports.",
])+q("strings is useful to…",[("Fully decompile modern C++","Limited.",False),("Quickly find URLs, commands, clues",True),("Replace a debugger always","No.",False)])),
("Static vs dynamic","Two lenses","concept · check",
"<p>Static reads code; dynamic watches behavior. Use both.</p>",
q("Dynamic analysis means…",[("Only reading assembly","Static.",False),("Running (safely) to observe behavior",True),("Deleting the binary","No.",False)])),
("Calling conventions & x86/x64 basics","Enough to navigate","concept · lab · check",
"<p>Registers, stack, calls/returns — enough to follow functions.</p>",
lab("Notes",[
"Label args/return in one function.",
"Find a strcmp/password check pattern.",
"Write what would patch/bypass in a crackme (lab).",
])+q("A call instruction typically…",[("Deletes the stack forever","No.",False),("Transfers control and sets up return",True),("Only works on Python","No.",False)])),
("Safe labs","Don't get owned","concept · check",
"<p>VMs, snapshots, no shared folders for malware, host isolation.</p>"+unlock_box("RE study groups and binary labs live in Discord."),
q("Analyzing malware on your daily driver…",[("Is recommended","Dangerous.",False),("Is a bad idea — use isolated labs",True),("Required","No.",False)])),
("From RE to bugs","Mindset bridge","concept · lab · check",
"<p>Look for unchecked copies, bad parsers, trust in inputs — lead-in to exploit modules.</p>",
lab("Bridge",[
"Find one unsafe pattern in a lab bin/source.",
"Describe the impact hypothesis.",
"Post a sanitized note in Discord.",
])+q("RE skills help vuln research by…",[("Replacing all web skills","Complement.",False),("Letting you understand real binary behavior",True),("Making scope optional","Never.",False)])),
]),
next_card("../exploit-development/linux-exploitation.html","Linux exploitation","Memory corruption intro.")
+prev_card("../ai-security/ai-red-teaming.html","AI red teaming","Optional prior."),
"csa:vulnerability-research/reverse-engineering-fundamentals.html","research/re","re-fundamentals",
tjson({"re":{"welcome":"RE triage.\\n","help":"file | strings | clear",
"cmds":{"file":"crackme: ELF 64-bit LSB pie executable, not stripped",
"strings":"Interesting: /bin/sh, strcmp, password_ok, TODO_remove_debug"},
"tasks":{"f":["file"],"s":["strings"]}}}),
xp=140,footer="Research · Isolated labs only"))

results.append(write_page(
"exploit-development/linux-exploitation.html","research","Linux exploitation",
"research / linux-exploit // act 3 · level 2",
"Memory corruption basics on intentionally vulnerable Linux labs.",
["→ Research"],["6 missions","~8 hrs","+140 XP"],
pack_missions([
("Memory layout","Where things live","concept · check",
"<p>Text, data, heap, stack. Corruption steers control flow.</p>",
q("Stack smashing classic goal?",[("Faster DNS","No.",False),("Overwrite control data (e.g. return address)",True),("Improve UX","No.",False)])),
("Buffer overflows","Lab classics","concept · terminal · lab · check",
"<p>Unbounded copies → overflow. Practice on protostar/phoenix-style labs.</p>",
term("exp","bash · exploit","Crash a lab bin","Type crash then eip",[
("c",'Crash (<code class="inl">crash</code>)'),
("e",'Control (<code class="inl">eip</code>)'),
],"exp@linux:~$")+lab("Authorized vulnerable VM",[
"Trigger a crash with a long input.",
"Note offset to control (lab guide).",
"Document mitigation flags you see.",
])+q("You practice exploits on…",[("Random internet hosts","Illegal.",False),("Intentionally vulnerable labs you own/are allowed",True),("Hospital life support","Never.",False)])),
("Mitigations intro","ASLR · NX · canaries","concept · check",
"<p>Modern defenses change exploit paths — learn to recognize them.</p>",
q("NX/DEP makes…",[("Stack always executable","Opposite.",False),("Data execution harder",True),("SSH faster","No.",False)])),
("Shellcode concepts","Payloads carefully","concept · check",
"<p>Understand conceptually; use lab payloads only. Prefer learning with safe challenges.</p>",
q("Running shellcode outside labs…",[("Is fine anywhere","Dangerous/illegal if unauthorized.",False),("Requires authorization / lab context",True),("Is required on prod","No.",False)])),
("Debugging workflow","Observe control","concept · lab · check",
"<p>gdb/gef/pwndbg: breakpoints, registers, stepi, examine memory.</p>"+unlock_box("Exploit lab nights live in Discord.")
+lab("gdb",[
"Break at main.",
"Inspect registers after crash.",
"Write a short lab note.",
])+q("Debuggers help you…",[("Skip understanding","No.",False),("See exact control-flow effects",True),("Bypass ROE","Never.",False)])),
("Writeups","Teach yourself","concept · lab · check",
"<p>Publish sanitized CTF/exploit writeups — specialist signal.</p>",
lab("Writeup",[
"Write one Linux exploit lab writeup.",
"Include mitigations discussion.",
"Share link in Discord.",
])+q("Good exploit writeups include…",[("Only the flag","Thin.",False),("Root cause, exploit steps, mitigations",True),("Live malware links","Dangerous.",False)])),
]),
next_card("../vulnerability-research/fuzzing-vulnerability-discovery.html","Fuzzing & discovery","Find crashes.")
+prev_card("../vulnerability-research/reverse-engineering-fundamentals.html","Reverse engineering","Read binaries."),
"csa:exploit-development/linux-exploitation.html","research/linux-exploit","linux-exploit",
tjson({"exp":{"welcome":"Linux exploit lab.\\n","help":"crash | eip | clear",
"cmds":{"crash":"Segmentation fault — input length 200 overflows buffer[64]",
"eip":"Saved return overwritten with 'BBBB' pattern — control achieved (lab)"},
"tasks":{"c":["crash"],"e":["eip"]}}}),
xp=140,footer="Research · Isolated labs only"))

results.append(write_page(
"vulnerability-research/fuzzing-vulnerability-discovery.html","research","Fuzzing & vulnerability discovery",
"research / fuzzing // act 3 · level 3",
"Automate crash finding — corpora, coverage, triage.",
["→ Research"],["6 missions","~7 hrs","+140 XP"],
pack_missions([
("Fuzzing idea","Mutate · feed · watch","concept · check",
"<p>Generate many inputs; catch crashes/hangs; minimize; root-cause.</p>",
q("Fuzzing is mainly…",[("Manual clicking only","Related but different.",False),("Automated atypical input testing",True),("Only social engineering","No.",False)])),
("Targets & harnesses","Make it fuzzable","concept · lab · check",
"<p>Library harnesses beat full networked apps at first. Persist corpora.</p>",
lab("Harness",[
"Pick a small parser lib/lab target.",
"Note how inputs enter.",
"Plan a harness entrypoint.",
])+q("A harness…",[("Is irrelevant","Needed.",False),("Feeds bytes into a target function safely",True),("Only draws UI","No.",False)])),
("Coverage guidance","Smarter fuzz","concept · terminal · check",
"<p>Coverage-guided fuzzers prefer inputs that hit new paths.</p>",
term("fuzz","bash · fuzz","Run a fuzz cycle","Type seed then crash",[
("s",'Seed (<code class="inl">seed</code>)'),
("c",'Crash (<code class="inl">crash</code>)'),
],"fuzz@lab:~$")+q("New coverage usually means…",[("Wasted cycles","Actually useful.",False),("You reached new code paths",True),("The fuzzer is broken","Not necessarily.",False)])),
("Crash triage","Signal vs noise","concept · lab · check",
"<p>Deduplicate, minimize, classify (null deref vs heap), prioritize.</p>",
lab("Triage",[
"Take one crash (lab).",
"Minimize input.",
"Guess bug class.",
])+q("Minimizing a crashing input helps…",[("Make crashes unreproducible","Opposite.",False),("Simplify root-cause analysis",True),("Increase CVSS automatically","No.",False)])),
("Sanitizers","ASan/UBSan","concept · check",
"<p>Build with sanitizers in lab to catch memory errors earlier.</p>"+unlock_box("Fuzzing corpora tips live in Discord."),
q("ASan helps detect…",[("CSS bugs","No.",False),("Many memory safety errors",True),("Only phishing","No.",False)])),
("Responsible discovery","What next","concept · check",
"<p>Crashes in real software → follow disclosure module. Don't exploit in the wild.</p>",
q("Finding a crash in real software…",[("Means immediate public exploit","Responsible disclosure.",False),("Should follow a disclosure process",True),("Means you own the company","No.",False)])),
]),
next_card("../exploit-development/binary-exploitation-advanced.html","Binary exploitation (advanced)","Bypass mitigations.")
+prev_card("../exploit-development/linux-exploitation.html","Linux exploitation","Overflows."),
"csa:vulnerability-research/fuzzing-vulnerability-discovery.html","research/fuzzing","fuzzing-ops",
tjson({"fuzz":{"welcome":"Fuzzer console.\\n","help":"seed | crash | clear",
"cmds":{"seed":"Corpus: 120 seeds · coverage edges +14%",
"crash":"NEW crash: heap-buffer-overflow in parse_header (ASan)"},
"tasks":{"s":["seed"],"c":["crash"]}}}),
xp=140,footer="Research · Isolated labs only"))

results.append(write_page(
"exploit-development/binary-exploitation-advanced.html","research","Binary exploitation (advanced)",
"research / bin-advanced // act 3 · level 4",
"Mitigation bypass concepts — still lab-only, ethics-first.",
["→ Research"],["6 missions","~10 hrs","+140 XP"],
pack_missions([
("Bypass landscape","Know the map","concept · check",
"<p>ASLR, PIE, canaries, RELRO, Fortify — each changes the game.</p>",
q("ASLR complicates…",[("Predictable addresses",True),("CSS colors","No.",False),("DNSSEC only","No.",False)])),
("Info leaks","Defeat ASLR","concept · lab · check",
"<p>Leaks let you compute addresses. Practice on advanced CTF bins.</p>",
lab("CTF lab",[
"Find a leak primitive in a writeup/lab.",
"Explain how it enables ROP.",
"Note partial RELRO implications.",
])+q("An info leak is valuable because…",[("It prints prettier errors","No.",False),("It reveals addresses for further exploitation",True),("It disables ethics","Never.",False)])),
("ROP concepts","Reuse code","concept · terminal · check",
"<p>Return-oriented programming chains existing gadgets when NX blocks shellcode.</p>",
term("rop","bash · rop","Build a tiny chain idea","Type gadgets then chain",[
("g",'Gadgets (<code class="inl">gadgets</code>)'),
("c",'Chain (<code class="inl">chain</code>)'),
],"exp@rop:~$")+q("ROP is used when…",[("NX prevents executing attacker data easily",True),("You only need HTML","No.",False),("ASLR is irrelevant always","ASLR still matters.",False)])),
("Heap intuition","Allocators bite","concept · check",
"<p>Use-after-free, double free concepts — learn with heap challenges carefully.</p>",
q("Use-after-free involves…",[("Using memory after free",True),("Only CSS floats","No.",False),("Mandatory in GRC","No.",False)])),
("Weaponization ethics","Hard stop","concept · check",
"<p>Building reliable exploits for unauthorized targets is illegal. Lab/CTF/bug bounty with rules only.</p>"+unlock_box("Advanced exploit clinics live in Discord.")
+q("Selling exploits for unauthorized use…",[("Is a cool side hustle","Illegal/harmful.",False),("Is illegal and against academy rules",True),("Required for Specialist rank","No.",False)])),
("Capstone lab","Prove skill","concept · lab · check",
"<p>Complete one advanced CTF/exploit challenge and write it up.</p>",
lab("Capstone",[
"Solve one advanced bin challenge.",
"Write a full writeup.",
"Share in Discord research channel.",
])+q("Specialist proof looks like…",[("Claims without artifacts","Weak.",False),("Writeups + responsible practice",True),("Bragging about crimes","Disqualifying.",False)])),
]),
next_card("../vulnerability-research/cve-research-disclosure.html","CVE research & disclosure","Tell vendors right.")
+prev_card("../vulnerability-research/fuzzing-vulnerability-discovery.html","Fuzzing","Find crashes."),
"csa:exploit-development/binary-exploitation-advanced.html","research/bin-advanced","bin-advanced",
tjson({"rop":{"welcome":"ROP workshop.\\n","help":"gadgets | chain | clear",
"cmds":{"gadgets":"Found: pop rdi; ret · system@libc candidate via leak",
"chain":"Plan: leak libc → compute system → ret2system with /bin/sh (lab)"},
"tasks":{"g":["gadgets"],"c":["chain"]}}}),
xp=140,footer="Research · Isolated labs only"))

results.append(write_page(
"vulnerability-research/cve-research-disclosure.html","research","CVE research & disclosure",
"research / disclosure // act 3 · level 5",
"From bug to coordinated disclosure — without becoming the incident.",
["→ Research","→ Specialist"],["5 missions","~4 hrs","+140 XP"],
pack_missions([
("Disclosure models","Coordinated first","concept · check",
"<p>Prefer coordinated/responsible disclosure. Know vendor channels & policies.</p>",
q("Best default for a real product bug?",[("Tweet full exploit same day","Harmful.",False),("Coordinated disclosure via vendor channel",True),("Sell to criminals","Illegal.",False)])),
("Report quality","Vendors are humans","concept · lab · check",
"<p>Repro, versions, environment, impact, suggested fix, your contact.</p>",
lab("Draft",[
"Write a disclosure report template.",
"Fill it with a lab bug as practice.",
"Find a real vendor security contact page (read-only).",
])+q("A vendor report needs…",[("Only insults","No.",False),("Clear repro + impact + versions",True),("Customer PII dumps","Minimize data.",False)])),
("CVE / numbering","When it applies","concept · check",
"<p>CNAs assign CVEs. Not every bug gets one. Don't invent fake CVE IDs.</p>",
q("Fake CVE numbers on resumes…",[("Are impressive","Fraud.",False),("Are dishonest",True),("Required","No.",False)])),
("Timelines & safe harbor","Read the policy","concept · check",
"<p>Many programs define deadlines & safe harbor — stay inside them.</p>"+unlock_box("Disclosure mentoring and peer review happen in Discord.")
+q("Safe harbor typically requires…",[("Ignoring scope","Opposite.",False),("Acting in good faith within program rules",True),("Public shaming first","No.",False)])),
("Academy finale","Specialist path","concept · lab · check",
"<p>You've reached the research endgame. Keep ethical. Jobs & advanced drops live in Discord.</p>",
lab("Finale",[
"Update portfolio with research writeups.",
"Set Specialist goals for next 90 days.",
"Join Discord and introduce your research focus.",
])+q("After this tree…",[("Attack hospitals for fun","Never.",False),("Keep learning ethically + use Discord for opportunities",True),("Stop documenting","Keep proof.",False)])),
]),
discord_card("Specialist drops · research clinics · jobs")
+prev_card("../exploit-development/binary-exploitation-advanced.html","Binary exploitation (advanced)","Bypasses."),
"csa:vulnerability-research/cve-research-disclosure.html","research/disclosure","cve-disclosure","{}",
xp=140,footer="Research · Coordinated disclosure"))

# ---------- COMMUNITY HUB ----------
results.append(write_page(
"community/discord-hub.html","community","Academy Discord HQ",
"community / discord // hq",
"Lessons live on Whop. Discord is your ops home — chapter drops, daily drills, job lounge, and check-ins.",
["→ Updates","→ Drills","→ Jobs"],["4 missions","~30 min","+50 XP"],
pack_missions([
("Why Discord","Ops home","concept · check",
"<p>Whop pages teach the curriculum. Discord keeps you current — feeds, chapter drops, accountability, and career ops.</p>"+unlock_box("Bookmark Discord. That’s where updates land first."),
q("In this academy, Discord is…",[("Optional spam","It's the ops home.",False),("Your ops home for updates, drills, and career channels",True),("Only for memes","More than that.",False)])),
("What lives there","Channels & feeds","concept · check",
"<p>Daily feeds · chapter announcements · track forums · job lounge · check-ins · peer reviews.</p>",
q("New chapter drops and job alerts show up…",[("Nowhere","In Discord.",False),("In Discord channels first",True),("Only on billboards","No.",False)])),
("How to intro","High-signal post","concept · lab · check",
"<p>Name · timezone · goal · current level · portfolio link · ask.</p>",
lab("Intro",[
"Copy your Start Here Discord intro.",
"Add 2 proof links.",
"Open Discord and post your intro.",
])+q("A strong intro includes…",[("Only 'hi'","Weak.",False),("Goal + level + proof links",True),("Your passwords","Never.",False)])),
("Rules of the road","Don't get banned","concept · check",
"<p>No illegal hacking help, no piracy dumps, no harassment. Lab talk stays ethical.</p>",
q("Asking for help hacking a real company without auth…",[("Is fine here","Against rules/law.",False),("Is forbidden",True),("Required for XP","No.",False)])),
]),
next_card("../career/resume-portfolio.html","Resume & portfolio","Job gate.")
+discord_card("Updates · drills · jobs lounge"),
"csa:community/discord-hub.html","community/discord-hub","discord-hq",
"{}",
xp=50,footer="Community · Open Discord",
legal="Community rules: authorized learning only. No illegal activity.")
)

# Patch evasion next card + start-here curriculum
evas = ROOT / "penetration-testing/evasion-techniques-breach.html"
txt = evas.read_text()
old = '<span class="ncard soon"><span class="k">Job gate</span><span class="t">Career & jobs</span><span class="d">Resume · interviews — coming soon.</span></span>'
new = (
    f'<a class="ncard" href="../career/resume-portfolio.html"><span class="k">Job gate</span>'
    f'<span class="t">Career & jobs</span><span class="d">Resume · interviews · certs.</span></a>'
    f'<a class="ncard dc" href="{DISCORD}" target="_blank" rel="noopener noreferrer">'
    f'<span class="k">Open Discord</span><span class="t">Academy HQ</span>'
    f'<span class="d">Updates · drills · jobs lounge</span></a>'
)
if old in txt:
    evas.write_text(txt.replace(old, new, 1))
    print("Patched evasion next cards")
else:
    print("WARN: evasion soon card not found")

sh = ROOT / "start-here.html"
st = sh.read_text()
st = st.replace('discord: ""    // e.g. "https://discord.gg/xxxxxxx"',
                f'discord: "{DISCORD}"')
# Update TRACKS/GOALS hrefs
replacements = [
( '{t:"SOC analyst fundamentals", h:null, hrs:5},\n      {t:"Incident response & DFIR", h:null, hrs:6},\n      {t:"Threat hunting",           h:null, hrs:6},\n      {t:"Detection engineering",    h:null, hrs:6}',
  '{t:"SOC analyst fundamentals", h:"defensive-security/soc-analyst-fundamentals.html", hrs:5},\n      {t:"Incident response & DFIR", h:"defensive-security/incident-response-dfir.html", hrs:6},\n      {t:"Threat hunting",           h:"defensive-security/threat-hunting.html", hrs:6},\n      {t:"Detection engineering",    h:"defensive-security/detection-engineering.html", hrs:6}'),
( '{t:"GRC fundamentals",      h:null, hrs:4},\n      {t:"Risk management",       h:null, hrs:5},\n      {t:"Compliance frameworks", h:null, hrs:5},\n      {t:"Security auditing",     h:null, hrs:5}',
  '{t:"GRC fundamentals",      h:"grc/grc-fundamentals.html", hrs:4},\n      {t:"Risk management",       h:"grc/risk-management.html", hrs:5},\n      {t:"Compliance frameworks", h:"grc/compliance-frameworks.html", hrs:5},\n      {t:"Security auditing",     h:"grc/security-auditing.html", hrs:5}'),
( '{t:"AI & LLM security fundamentals", h:null, hrs:5},\n      {t:"AI red teaming",                 h:null, hrs:6}',
  '{t:"AI & LLM security fundamentals", h:"ai-security/ai-llm-security-fundamentals.html", hrs:5},\n      {t:"AI red teaming",                 h:"ai-security/ai-red-teaming.html", hrs:6}'),
( '{t:"Resume & portfolio for cyber roles", h:null, hrs:3},\n    {t:"Interview prep",                     h:null, hrs:3},\n    {t:"Certification roadmap",              h:null, hrs:2}',
  '{t:"Resume & portfolio for cyber roles", h:"career/resume-portfolio.html", hrs:3},\n    {t:"Interview prep",                     h:"career/interview-prep.html", hrs:3},\n    {t:"Certification roadmap",              h:"career/certification-roadmap.html", hrs:2}'),
( '{t:"Bug bounty fundamentals",        h:null, hrs:3},\n    {t:"Recon & asset discovery",        h:null, hrs:5},\n    {t:"Writing reports that get paid",  h:null, hrs:3},\n    {t:"Advanced bounty techniques",     h:null, hrs:6}',
  '{t:"Bug bounty fundamentals",        h:"bug-bounty/bug-bounty-fundamentals.html", hrs:3},\n    {t:"Recon & asset discovery",        h:"bug-bounty/recon-asset-discovery.html", hrs:5},\n    {t:"Writing reports that get paid",  h:"bug-bounty/writing-reports.html", hrs:3},\n    {t:"Advanced bounty techniques",     h:"bug-bounty/advanced-bounty-techniques.html", hrs:6}'),
( '{t:"Getting your first client",     h:null, hrs:3},\n    {t:"Pricing & contracts",           h:null, hrs:3},\n    {t:"Building a portfolio",          h:null, hrs:3},\n    {t:"Client management & red flags",  h:null, hrs:2}',
  '{t:"Getting your first client",     h:"freelancing/first-client.html", hrs:3},\n    {t:"Pricing & contracts",           h:"freelancing/pricing-contracts.html", hrs:3},\n    {t:"Building a portfolio",          h:"freelancing/building-portfolio.html", hrs:3},\n    {t:"Client management & red flags",  h:"freelancing/client-management.html", hrs:2}'),
( '{t:"Reverse engineering fundamentals",   h:null, hrs:8},\n    {t:"Linux exploitation",                 h:null, hrs:8},\n    {t:"Fuzzing & vulnerability discovery",  h:null, hrs:7},\n    {t:"Binary exploitation (advanced)",     h:null, hrs:10},\n    {t:"CVE research & disclosure",          h:null, hrs:4}',
  '{t:"Reverse engineering fundamentals",   h:"vulnerability-research/reverse-engineering-fundamentals.html", hrs:8},\n    {t:"Linux exploitation",                 h:"exploit-development/linux-exploitation.html", hrs:8},\n    {t:"Fuzzing & vulnerability discovery",  h:"vulnerability-research/fuzzing-vulnerability-discovery.html", hrs:7},\n    {t:"Binary exploitation (advanced)",     h:"exploit-development/binary-exploitation-advanced.html", hrs:10},\n    {t:"CVE research & disclosure",          h:"vulnerability-research/cve-research-disclosure.html", hrs:4}'),
]
for a,b in replacements:
    if a not in st:
        print("WARN missing block:\n", a[:80])
    else:
        st = st.replace(a,b,1)
        print("Patched curriculum block")

# Update Discord CTA copy on start-here
st = st.replace(
    '<span class="t">Join Discord</span>\n      <span class="d">Post intro · job alerts · get unstuck</span>',
    '<span class="t">Open Discord</span>\n      <span class="d">Updates · drills · jobs lounge</span>')
st = st.replace(
    'Job Ready:</strong> Core + track missions cleared · resume/portfolio page · Discord apply.',
    'Job Ready:</strong> Core + track missions cleared · resume/portfolio · open Discord & apply.')
sh.write_text(st)
print("start-here patched")

print("TOTAL", len(results), "OK", sum(1 for x in results if x), "FAIL", sum(1 for x in results if not x))
if not all(results):
    raise SystemExit(1)
print("ALL_GOOD")
