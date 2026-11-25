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
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls)+"</urlset>\n"
(ROOT/"sitemap.xml").write_text(xml,encoding="utf-8")
print(f"Generated {len(urls)-7} work pages")
