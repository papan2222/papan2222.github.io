"""Regenerate author collections from quotation data."""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://papan2222.github.io"
SLUGS = {"R. W. Emerson":"emerson","Thoreau":"thoreau","Oscar Wilde":"oscar-wilde","Mark Twain":"mark-twain","Nietzsche":"nietzsche","Goethe":"goethe","Ambrose Bierce":"ambrose-bierce","Eric Hoffer":"eric-hoffer","William James":"william-james","Schopenhauer":"schopenhauer"}
SHORT = {"R. W. Emerson":"エマソン","Thoreau":"ソロー","Nietzsche":"ニーチェ","Goethe":"ゲーテ","Schopenhauer":"ショーペンハウアー"}

def h(value):
    return html.escape(str(value), quote=True)

def generate():
    quotes = json.loads((ROOT/"quotes.json").read_text(encoding="utf-8"))
    profiles = json.loads((ROOT/"quotes/authors.json").read_text(encoding="utf-8"))
    groups = {}
    for q in quotes:
        groups.setdefault(q["author"], []).append(q)
    if not set(groups) <= set(SLUGS):
        raise ValueError("Unregistered author slug")
    def name(a):
        return SHORT.get(a, profiles.get(a, {}).get("ja", a))
    links = "".join(f'<li><a href="/quotes/authors/{SLUGS[a]}/">{h(name(a))}の英語名言</a>（{len(rows)}作品）</li>' for a, rows in groups.items())
    def page(path, title, desc, body):
        url = BASE + path
        content = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta name="description" content="{h(desc)}"><link rel="canonical" href="{url}"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website"><link rel="stylesheet" href="/quotes/works/style.css"><link rel="stylesheet" href="/quotes/authors/style.css"></head><body><main><header><a href="/">ホーム</a> ／ <a href="/quotes/">英語名言</a> ／ <a href="/quotes/authors/">作者別特集</a></header>{body}</main></body></html>'
        out = ROOT / path.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    for a, rows in groups.items():
        p = profiles.get(a, {})
        title = f"{name(a)}の英語名言 {len(rows)}選"
        cards = []
        for q in rows:
            tips = "".join(f"<li>{h(t)}</li>" for t in q.get("tips", []))
            cards.append(f'<article><div class="quotation" lang="en">{h(q["en"])}</div><p class="translation">{h(q["jp"])}</p><details><summary>ENGLISH TIP</summary><ul>{tips}</ul></details><a class="quote-link" href="/quotes/works/{h(q["id"])}/">個別ページ ↗</a></article>')
        body = f'<h1>{h(title)}</h1><p>{h(p.get("ja",a))}（{h(a)}、{h(p.get("years",""))}）</p><p>{h(p.get("bio",""))}</p><p>英語原文と日本語訳を読み、ENGLISH TIPで単語・熟語・文法を学べます。</p><small>原典・作者への帰属は未確認のものを含みます。日本語訳はAI支援を含みます。</small>{"".join(cards)}<h2>ほかの作者の英語名言</h2><ul class="authors-list">{links}</ul>'
        page(f"/quotes/authors/{SLUGS[a]}/",title+"｜日本語訳・英語解説",f"{name(a)}の英語名言を日本語訳と語彙・文法の解説で紹介。",body)
    page("/quotes/authors/","偉人の英語名言・作者別特集","思想家・作家の英語名言と日本語訳。",f'<h1>偉人の英語名言・作者別特集</h1><p>全{len(quotes)}作品</p><ul class="authors-list">{links}</ul>')

if __name__ == "__main__":
    generate()
