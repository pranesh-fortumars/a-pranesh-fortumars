#!/usr/bin/env python3
"""Render animated SVG GitHub profile cards. STATIC=1 disables motion for screenshots."""
import os, json, base64, subprocess
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict, Counter
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"cards"; DATA=ROOT/"data"/"contributions.json"
USER=os.getenv("GITHUB_USERNAME","pranesh-fortumars"); STATIC=os.getenv("STATIC","").lower() in {"1","true","yes"}
CYAN,PURPLE,RED="#00F0FF","#7A00FF","#FF003C"; BG,WHITE,MUTED="#05070B","#F4FAFF","#93A4B8"
FONT="ProfileEmbedded, Geist, 'Geist Mono', Arial, sans-serif"; FONT_CSS=""
def subset_font():
    source=Path(os.getenv("PROFILE_FONT_FILE","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    target=OUT/".profile-subset.woff"
    if not source.is_file(): return ""
    glyphs="PRANESH S Software Development Team Lead Cybersecurity AI Blockchain Cloud Full Stack GitHub Contributions January February March April May June July August September October November December 0123456789"
    try:
        subprocess.run(["pyftsubset",str(source),"--output-file="+str(target),"--flavor=woff","--text="+glyphs,"--layout-features=*"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        encoded=base64.b64encode(target.read_bytes()).decode("ascii"); target.unlink(missing_ok=True)
        return "@font-face{font-family:ProfileEmbedded;src:url(data:font/woff;base64,"+encoded+") format('woff');}"
    except (OSError,subprocess.CalledProcessError): return ""
def load_metrics():
    raw=json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"weeks":[],"total":0}
    if "weeks" in raw: return raw
    cal=raw.get("data",{}).get("user",{}).get("contributionsCollection",{}).get("contributionCalendar",{})
    return {"total":cal.get("totalContributions",0),"weeks":[{"days":[{"date":d["date"],"count":d["contributionCount"]} for d in w.get("contributionDays",[])]} for w in cal.get("weeks",[])]}
def document(title,body,height=250,delay=0):
    motion="" if STATIC else f"""
    @keyframes card-enter{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
    .card{{animation:card-enter .8s ease-out both;animation-delay:{delay}s}}
    @media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}} animate,animateTransform,set{{display:none!important}}}}
    """
    css=FONT_CSS+f"text{{font-family:{FONT}}}"+motion
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img">
    <title>{escape(title)}</title><style>{css}</style>
    <defs><linearGradient id="edge"><stop stop-color="{CYAN}"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="{RED}"/></linearGradient><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{CYAN}" stroke-opacity=".06"/></pattern></defs>
    <g class="card"><rect x="8" y="8" width="984" height="{height-16}" rx="22" fill="{BG}" stroke="url(#edge)" stroke-width="2"/><rect x="9" y="9" width="982" height="{height-18}" rx="21" fill="url(#grid)"/>{body}</g></svg>'''
def save(name,content): (OUT/name).write_text(content,encoding="utf-8")
def main():
    global FONT_CSS
    OUT.mkdir(parents=True,exist_ok=True); FONT_CSS=subset_font(); metrics=load_metrics()
    days=sorted((d for w in metrics.get("weeks",[]) for d in w.get("days",[])),key=lambda x:x["date"])
    save("01-hero.svg",document("Pranesh S — Software Development Team Lead",f'''
    <text x="56" y="70" fill="{CYAN}" font-size="15" letter-spacing="5">PROFILE // SYSTEM ONLINE</text>
    <text x="52" y="148" fill="{WHITE}" font-size="68" font-weight="800">PRANESH S</text>
    <text x="56" y="190" fill="{MUTED}" font-size="21">Software Development Team Lead · Cybersecurity · AI · Blockchain</text>
    <path d="M56 211H290" stroke="{CYAN}" stroke-width="3"/>''',260,0))
    tiles=[]
    for i,(label,sub,url,color) in enumerate([("GITHUB","Code · Open source",f"https://github.com/{USER}",CYAN),("LINKEDIN","Engineering · Network","https://www.linkedin.com/in/pranesh-s-ps34101136/",PURPLE),("PORTFOLIO","Explore my work","https://async-2.vercel.app/",RED)]):
        x=20+i*330
        tiles.append(f'<a href="{url}"><rect x="{x}" y="12" width="315" height="104" rx="16" fill="#0B111A" stroke="{color}" stroke-width="2"/><text x="{x+20}" y="52" fill="{color}" font-size="21" font-weight="700">{label}</text><text x="{x+20}" y="82" fill="{MUTED}" font-size="15">{sub}</text><text x="{x+278}" y="70" fill="{color}" font-size="24">↗</text></a>')
    save("02-links.svg",document("Connect with Pranesh","".join(tiles),140,1))
    monthly=defaultdict(int); weekdays=Counter(); counts={}
    for d in days:
        dt=date.fromisoformat(d["date"]); count=int(d.get("count",0)); monthly[d["date"][:7]]+=count; weekdays[dt.strftime("%A")]+=count; counts[dt]=count
    cursor=date.today() if counts.get(date.today(),0)>0 else date.today()-timedelta(days=1); streak=0
    while counts.get(cursor,0)>0: streak+=1; cursor-=timedelta(days=1)
    active=sum(v>0 for v in counts.values()); busiest=max(weekdays,key=weekdays.get) if weekdays else "—"
    months=sorted(monthly)[-12:]; peak=max([monthly[x] for x in months] or [1]); bars=[]
    for i,month in enumerate(months):
        h=90*monthly[month]/peak; x=60+i*74
        smil="" if STATIC else f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".8s" begin="{2+i*.08}s" fill="freeze"/>'
        bars.append(f'<rect x="{x}" y="{160-h:.1f}" width="42" height="{h:.1f}" rx="5" fill="{CYAN}">{smil}</rect><text x="{x+21}" y="180" text-anchor="middle" fill="{MUTED}" font-size="10">{month[5:]}</text>')
    body=f'<text x="42" y="45" fill="{CYAN}" font-size="14" letter-spacing="4">CONTRIBUTION INTELLIGENCE // LAST 12 MONTHS</text><text x="42" y="86" fill="{WHITE}" font-size="29">{metrics.get("total",0):,} contributions</text><path d="M50 160H950" stroke="{MUTED}" opacity=".25"/>{"".join(bars)}'
    for x,label,color in [(42,f"{streak} day streak",CYAN),(362,f"{active} active days",PURPLE),(682,"Busiest: "+busiest,RED)]:
        body+=f'<rect x="{x}" y="205" width="275" height="40" rx="10" fill="#0B111A" stroke="{color}"/><text x="{x+16}" y="231" fill="{WHITE}" font-size="15">{escape(label)}</text>'
    save("03-activity.svg",document("Monthly contributions, streak, active days and busiest day",body,270,2))
    repos=[("HydraDragonAntivirus","Security tooling and antivirus research","Python"),("decentralized-energy-marketplace","Blockchain-powered energy marketplace","Blockchain"),("hotel-management","Hotel operations and management","Full stack"),("lms","Learning management system","Full stack")]
    for i,(name,desc,lang) in enumerate(repos):
        color=[CYAN,PURPLE,RED][i%3]
        body=f'<text x="42" y="48" fill="{color}" font-size="14" letter-spacing="4">FEATURED REPOSITORY // {i+1:02d}</text><text x="42" y="110" fill="{WHITE}" font-size="34" font-weight="700">{escape(name)}</text><text x="42" y="157" fill="{MUTED}" font-size="18">{escape(desc)}</text><rect x="42" y="190" width="150" height="36" rx="18" fill="{color}" fill-opacity=".12" stroke="{color}"/><text x="117" y="213" fill="{color}" text-anchor="middle" font-size="14">{lang}</text><a href="https://github.com/{USER}/{name}"><text x="950" y="216" fill="{color}" text-anchor="end" font-size="16">OPEN REPOSITORY ↗</text></a>'
        save(f"{4+i:02d}-repo-{name.lower()}.svg",document(name+" repository",body,250,3+i*.75))
    recent=days[-371:]; offset=(date.fromisoformat(recent[0]["date"]).weekday()+1)%7 if recent else 0
    maximum=max([int(d.get("count",0)) for d in recent] or [1]); cells=[]
    for i,d in enumerate(recent):
        col,row=(offset+i)//7,(offset+i)%7; n=int(d.get("count",0)); opacity=.08 if n==0 else .25+.75*n/maximum
        cells.append(f'<rect x="{54+col*17}" y="{82+row*18}" width="12" height="12" rx="3" fill="{CYAN}" opacity="{opacity:.2f}"><title>{d["date"]}: {n} contributions</title></rect>')
    save("08-contributions.svg",document("GitHub contribution graph in cyan brand colour",f'<text x="42" y="38" fill="{CYAN}" font-size="14" letter-spacing="4">CONTRIBUTION MATRIX // BRAND SIGNAL</text>{"".join(cells)}<text x="950" y="220" text-anchor="end" fill="{CYAN}" font-size="13">{metrics.get("total",0):,} contributions · {USER}</text>',260,7))
    print("Rendered",len(list(OUT.glob("*.svg")),"SVG cards")
if __name__=="__main__": main()
