"""Generate diary and senryu individual pages from the source galleries."""
import re
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://papan2222.github.io"
def read(path):
    return (ROOT/path).read_text(encoding="utf-8")
def write(path, content):
    out = ROOT/path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
def h(value):
    return html.escape(str(value), quote=True)
def plain(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
def validate(rows):
    ids = [i for i, _ in rows]
    if not ids or len(ids) != len(set(ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", i) for i in ids):
        raise ValueError("Missing, duplicate or invalid work ID")
    return ids
def page_head(section, ident, title, desc, label, image, css):
    url = f"{BASE}/{section}/works/{ident}/"
    image_tag = f'<meta property="og:image" content="{h(BASE+image)}">' if image.startswith("/") else ""
    return f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}｜{h(label)}</title><meta name="description" content="{h(desc)}"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{url}">{image_tag}<meta name="twitter:card" content="summary_large_image">{css}</head><body>'
def nav(section, ids, i):
    path = lambda j: f"/{section}/works/{ids[j]}/"
    prev = f'<a href="{path(i-1)}">← 前の作品</a>' if i else ""
    nxt = f'<a href="{path(i+1)}">次の作品 →</a>' if i+1 < len(ids) else ""
    rand = f'<a class="random" id="random-next" href="{path((i+1)%len(ids))}">ランダムに次の作品へ</a>' if len(ids)>1 else ""
    return f'<nav class="work-nav" aria-label="作品移動">{prev}<a href="/{section}/">作品一覧</a>{nxt}{rand}</nav>'
def random_script(section, ids):
    write(f"{section}/works/random.js", "const ids="+json.dumps(ids)+";const a=document.getElementById('random-next');const id=location.pathname.split('/').filter(Boolean).pop();const pool=ids.filter(x=>x!==id);if(a&&pool.length)a.href='/"+section+"/works/'+pool[Math.floor(Math.random()*pool.length)]+'/';")
def blog():
    source = read("blog/index.md")
    pattern = r'<article class="work" id="([^"]+)">([\s\S]*?)</article>'
    rows = re.findall(pattern, source)
    ids = validate(rows)
    random_script("blog", ids)
    for i, (ident, body) in enumerate(rows):
        ja = " ".join(plain(p) for p in re.findall(r'<p class="ja">([\s\S]*?)</p>', body))
        en = " ".join(plain(p) for p in re.findall(r'<p class="en">([\s\S]*?)</p>', body))
        if not ja or not en:
            raise ValueError("Missing diary text: "+ident)
        image = re.search(r'<img[^>]*src="([^"]+)"', body)[1]
        title = re.sub(r"\s+", " ", ja.lstrip("🐼 "))[:65]
        desc = re.sub(r"\s+", " ", ja+" "+en+" 英会話表現・発音記号・音声付き。")[:160]
        card = re.sub(r'<a class="detail-link"[^>]*>[\s\S]*?</a>', '', body)
        card = re.sub(r'<a href="#[^"]+">(<img[^>]*>)</a>', r'\1', card)
        card = card.replace('loading="lazy"', 'loading="eager"').replace('<details class="tip">', '<details class="tip" open>')
        if 'class="audio"' not in card:
            card += '<div class="audio"></div>'
        if len(re.findall(r'class="wordaudio"', card)) != len(re.findall(r'class="term"', card)):
            raise ValueError("Mismatched vocabulary audio controls: "+ident)
        page = page_head("blog", ident, title, desc, "パンダの笑える英語日記", image, '<link rel="stylesheet" href="/blog/works/style.css">')
        page += f'<header><a href="/">ホーム</a> ／ <a href="/blog/">笑える英語日記</a><h1>{h(title)}</h1></header><main><article class="work">{card}</article>{nav("blog",ids,i)}<p><a href="/animalenglish/">どうぶつ英単語</a> ／ <a href="/quotes/">英語名言</a></p></main><script src="/audio/player.js"></script><script src="/blog/works/audio.js"></script><script src="/blog/works/random.js"></script></body></html>'
        write(f"blog/works/{ident}/index.html", page)
    def link(m):
        ident, body = m.groups()
        body = re.sub(r'<a class="detail-link"[^>]*>[\s\S]*?</a>', '', body)
        body += f'<a class="detail-link" href="/blog/works/{ident}/" aria-label="個別ページを開く">↗ 個別ページ</a>'
        return f'<article class="work" id="{ident}">{body}</article>'
    write("blog/index.md", re.sub(pattern, link, source))
    print("Diary:", len(ids), "pages")
def senryu():
    source = read("senryu/index.md")
    pattern = r'<div class="card" id="work-([^"]+)">([\s\S]*?)(?=<div class="card" id="work-|$)'
    rows = re.findall(pattern, source)
    ids = validate(rows)
    random_script("senryu", ids)
    css = re.search(r'<style>([\s\S]*?)</style>', read("_layouts/senryu.html"))[1]
    write("senryu/works/style.css", css+"\n.site-title{font-size:20px;font-weight:500}.poem p{margin:10px 0}")
    for i, (ident, body) in enumerate(rows):
        poem = re.search(r'<p class="poem">([\s\S]*?)</p>', body)[1]
        lines = [plain(x) for x in poem.splitlines() if plain(x)]
        if len(lines) < 4:
            raise ValueError("Incomplete bilingual poem: "+ident)
        title = " ".join(lines[:3])
        picture = re.search(r'<img[^>]*>', body)[0].replace('loading="lazy"', 'loading="eager"')
        image = re.search(r'src="([^"]+)"', picture)[1]
        tip = re.search(r'<details class="english-tip"[^>]*>[\s\S]*?</details>', body)
        notes = tip[0].replace('<details class="english-tip">','<details class="english-tip" open>') if tip else ""
        card = picture+'<div class="poem"><p lang="ja">'+h("\n".join(lines[:3]))+'</p><p lang="en">'+h("\n".join(lines[3:]))+'</p></div>'+notes
        page = page_head("senryu", ident, title, " / ".join(lines), "パンダの英語川柳", image, '<link rel="stylesheet" href="/senryu/works/style.css">')
        page += f'<nav class="home-only"><a href="/senryu/">パンダの英語川柳・作品一覧</a></nav><main><h1 class="site-title">{h(title)}</h1><div class="cards"><article class="card">{card}</article></div>{nav("senryu",ids,i)}</main><script src="/senryu/works/random.js"></script></body></html>'
        write(f"senryu/works/{ident}/index.html", page)
    def link(m):
        ident, body = m.groups()
        body = re.sub(r'(<a class="image-link"[^>]*href=")[^"]+(")',lambda x:x[1]+f"/senryu/works/{ident}/"+x[2],body)
        body = re.sub(r'(<div class="detail-link"><a href=")[^"]+(")',lambda x:x[1]+f"/senryu/works/{ident}/"+x[2],body)
        if 'class="detail-link"' not in body:
            ending = re.search(r'</div>\s*(?:</div>\s*)?$', body)
            if ending is None:
                raise ValueError("Missing senryu card closing tag: "+ident)
            body = body[:ending.start()]+f'<div class="detail-link"><a href="/senryu/works/{ident}/" aria-label="作品を個別表示" title="個別ページ">↗</a></div>'+body[ending.start():]
        return f'<div class="card" id="work-{ident}">'+body
    write("senryu/index.md", re.sub(pattern, link, source))
    print("Senryu:", len(ids), "pages")
if __name__ == "__main__":
    blog()
    senryu()
