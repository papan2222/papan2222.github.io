"""Generate static work pages and sitemap. Run from repository root."""
import json, html, re
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent
BASE="https://papan2222.github.io"
def h(s): return html.escape(str(s), quote=True)
urls=[BASE+x for x in ("/","/blog/","/quotes/","/senryu/","/pandalife/","/game/","/animalenglish/")]
for section, source in (("pandalife","works.json"),("game","gallery.json")):
    rows=json.loads((ROOT/section/source).read_text(encoding="utf-8"))
    seen=set()
    for w in rows:
        ident=w["id"] if section=="pandalife" else Path(w["file"]).stem
        if not re.fullmatch(r"[A-Za-z0-9_-]+",ident) or ident in seen:
            raise ValueError("Invalid or duplicate ID: "+ident)
        seen.add(ident)
        lines=w.get("text",[]) if section=="pandalife" else [w.get("captionJa",""),w.get("captionEn","")]
        lines=[s for s in lines if s]
        if not lines: continue
        title=w.get("title") or lines[0]
        desc=" ".join(lines)[:160]
        images=w.get("images",[]) if section=="pandalife" else [w["file"]]
        url=f"{BASE}/{section}/works/{ident}/"
        legacy=f"/{section}/?id={quote(ident)}"
        pics="".join(f'<img src="/{section}/{h(quote(src,safe="/"))}" alt="{h(w.get("alt") or title)}" loading="lazy">' for src in images)
        paras="".join(f'<p lang="{"ja" if re.search(r"[ぁ-んァ-ヶ一-龯]",s) else "en"}">{h(s)}</p>' for s in lines)
        notes="".join(f"<li>{h(s)}</li>" for s in w.get("study",[]))
        study=f"<h2>英語学習ポイント</h2><ul>{notes}</ul>" if notes else ""
        page=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}｜パンダの英語作品</title><meta name="description" content="{h(desc)}"><link rel="canonical" href="{url}"><style>body{{margin:24px auto;padding:0 16px;max-width:760px;font:17px/1.8 system-ui,sans-serif;background:#f5f0e7;color:#39342e}}img{{width:100%;height:auto;border-radius:12px}}p{{white-space:pre-wrap}}a{{color:#285c87}}</style></head><body><nav><a href="/{section}/">作品一覧</a> · <a href="/">ホーム</a></nav><main><h1>{h(title)}</h1>{pics}{paras}{study}<p><a href="{legacy}">ギャラリーで作品を見る・音声を聞く</a></p></main></body></html>'''
        out=ROOT/section/"works"/ident/"index.html"
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(page,encoding="utf-8")
        urls.append(url)
# Include existing senryu and vocabulary pages in every regeneration.
for p in sorted((ROOT/"senryu"/"works").glob("*/index.html")):
    urls.append(BASE+"/"+p.parent.relative_to(ROOT).as_posix()+"/")
for p in sorted((ROOT/"animalenglish"/"word").glob("*.html")):
    urls.append(BASE+"/"+p.relative_to(ROOT).as_posix())

# Static quotations: full text and learning notes are available without JavaScript.
quotes=json.loads((ROOT/"quotes.json").read_text(encoding="utf-8"))
authors=json.loads((ROOT/"quotes"/"authors.json").read_text(encoding="utf-8"))
ids=[q["id"] for q in quotes]
if len(ids)!=len(set(ids)) or any(not re.fullmatch(r"q[0-9]+",i) for i in ids):
    raise ValueError("Invalid or duplicate quotation IDs")
qroot=ROOT/"quotes"/"works"
qroot.mkdir(parents=True,exist_ok=True)
css=":root{color-scheme:dark;--ink:#f4eedf;--muted:#b9bdc5;--gold:#d9ba7c;--line:#77674c}*{box-sizing:border-box}body{min-height:100vh;margin:0;color:var(--ink);font-family:system-ui,sans-serif;background:radial-gradient(ellipse at 15% 0%,#303d50 0%,transparent 55%),radial-gradient(ellipse at 100% 90%,#34312e 0%,transparent 48%),#182330}main{max-width:760px;margin:auto;padding:28px 22px 42px}header{border-bottom:1px solid #ffffff20;padding-bottom:18px}h1{font-family:Georgia,\"Yu Mincho\",serif;font-size:20px;font-weight:500;letter-spacing:.08em;margin:0 0 12px}a{color:var(--gold);text-underline-offset:4px}header a{font-size:13px}article{position:relative;margin:28px 0 18px;padding:clamp(20px,5vw,42px);border:1px solid #a58b574d;border-radius:8px;background:linear-gradient(145deg,#263343,#202b39);box-shadow:0 16px 48px #080d1938}article:before{content:\"“\";display:block;color:var(--gold);font:64px/.65 Georgia,serif;margin:0 0 18px}#en{font-family:Georgia,\"Times New Roman\",serif;font-size:clamp(23px,5vw,33px);line-height:1.5;overflow-wrap:anywhere}#jp{color:#e1dfd8;line-height:1.9;margin-top:24px}#author{text-align:right;color:var(--gold);font-family:Georgia,\"Yu Mincho\",serif;line-height:1.6}#tips{margin-top:28px;padding:18px 20px;background:#121c2a66;border-left:2px solid var(--gold);border-radius:0 5px 5px 0}#tips h2{margin:0 0 10px;color:var(--gold)}#tip-list{margin:0;color:#e2e5eb}#profile{border-top:1px solid #ffffff20;padding-top:16px;margin-bottom:0}nav{display:flex;justify-content:center;margin:20px 0 24px}button{font:inherit;font-size:15px;letter-spacing:.04em;color:#192330;background:#d9ba7c;border:1px solid #e8ce99;border-radius:6px;padding:13px 25px;cursor:pointer;min-height:48px}button:hover{background:#ecd09a}button:disabled{opacity:.45;cursor:default}a:focus-visible,button:focus-visible{outline:2px solid #fff;outline-offset:4px}small{color:var(--muted);font-size:12px;line-height:1.7;display:block}@media(max-width:480px){main{padding:20px 12px 32px}article{margin-top:20px;padding:22px 18px}#tips{padding:14px 12px}nav button{width:100%}}"
(qroot/"style.css").write_text(css+"\nnav{gap:12px;flex-wrap:wrap}nav a{padding:10px 14px;border:1px solid #77674c;border-radius:5px}h1#en{font-weight:400;margin:0;letter-spacing:0}",encoding="utf-8")
(qroot/"random.js").write_text("const ids="+json.dumps(ids,separators=(",",":"))+";document.getElementById('random-next').addEventListener('click',()=>{const current=location.pathname.split('/').filter(Boolean).pop();const pool=ids.filter(i=>i!==current);if(pool.length)location.href='/quotes/works/'+pool[Math.floor(Math.random()*pool.length)]+'/'});",encoding="utf-8")
groups={}
for n,q in enumerate(quotes):
    ident=q["id"]; author=q["author"]; profile=authors.get(author,{})
    name=profile.get("ja",author)
    author_slugs={"R. W. Emerson":"emerson","Thoreau":"thoreau","Oscar Wilde":"oscar-wilde","Mark Twain":"mark-twain","Nietzsche":"nietzsche","Goethe":"goethe","Ambrose Bierce":"ambrose-bierce","Eric Hoffer":"eric-hoffer","William James":"william-james","Schopenhauer":"schopenhauer"}
    author_link=f'<a href="/quotes/authors/{author_slugs[author]}/">{h(name)}の名言一覧</a>' if author in author_slugs else ""
    groups.setdefault(author,[]).append(q)
    url=f"{BASE}/quotes/works/{ident}/"
    title=f"{q['en'][:90]}｜{name}の英語名言"
    desc=f"{q['jp']} 英語原文・語彙・文法の解説。{name}の名言。"[:160]
    notes="".join(f"<li>{h(t)}</li>" for t in q.get("tips",[]))
    bio=h((profile.get("years","")+" "+profile.get("bio","")).strip())
    prev=f'<a href="/quotes/works/{ids[n-1]}/">← 前の名言</a>' if n else ""
    nxt=f'<a href="/quotes/works/{ids[n+1]}/">次の名言 →</a>' if n+1<len(ids) else ""
    page=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta name="description" content="{h(desc)}"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/quotes/works/style.css"></head><body><main><header><a href="/">ホーム</a> ／ <a href="/quotes/">パンダの英語名言</a> ／ <a href="/quotes/works/">全名言一覧</a></header><article><h1 id="en" lang="en">{h(q["en"])}</h1><p id="jp">{h(q["jp"])}</p><p id="author">{h(name)} ／ {h(author)}</p><section id="tips"><h2 style="font-size:13px;letter-spacing:.06em">ENGLISH TIP</h2><ul id="tip-list" style="padding-left:20px;line-height:1.8;font-size:15px">{notes}</ul></section><p id="profile" style="font-size:14px;color:#b9bdc5;line-height:1.7">{bio}</p><p>{author_link}</p></article><nav aria-label="名言の移動">{prev}<a href="/quotes/works/">一覧</a>{nxt}</nav><nav><button id="random-next" type="button">次の名言へ（ランダム） →</button></nav><small>原典・作者への帰属は未確認のものを含みます。日本語訳はAI支援を含みます。</small></main><script src="/quotes/works/random.js" defer></script></body></html>'''
    out=qroot/ident/"index.html"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(page,encoding="utf-8")
    urls.append(url)
# Author-grouped HTML directory provides crawlable links to every quotation.
sections=[]
for author,items in groups.items():
    name=authors.get(author,{}).get("ja",author)
    links="".join(f'<li><a href="/quotes/works/{q["id"]}/" lang="en">{h(q["en"])}</a></li>' for q in items)
    sections.append(f"<section><h2>{h(name)} ({len(items)})</h2><ul>{links}</ul></section>")
directory=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>英語名言 全作品・作者別一覧｜パンダの英語名言</title><meta name="description" content="英語名言の作者別一覧。英語原文、日本語訳、語彙・文法解説へのリンク。"><link rel="canonical" href="{BASE}/quotes/works/"><link rel="stylesheet" href="/quotes/works/style.css"></head><body><main><header><a href="/">ホーム</a> ／ <a href="/quotes/">検索・ランダム表示</a></header><h1>英語名言 全作品・作者別一覧</h1>{"".join(sections)}</main></body></html>'''
(qroot/"index.html").write_text(directory,encoding="utf-8")
urls.append(BASE+"/quotes/works/")

for p in sorted((ROOT/"blog"/"works").glob("*/index.html")):
    urls.append(BASE+"/"+p.parent.relative_to(ROOT).as_posix()+"/")
# Keep author feature pages discoverable on sitemap regeneration.
for p in sorted((ROOT/"quotes"/"authors").rglob("index.html")):
    urls.append(BASE+"/"+p.parent.relative_to(ROOT).as_posix()+"/")
urls=list(dict.fromkeys(urls))
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls)+"</urlset>\n"
(ROOT/"sitemap.xml").write_text(xml,encoding="utf-8")
print(f"Generated {len(urls)-7} work pages")
