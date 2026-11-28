"""Build vocabulary collections from published vocabulary cards."""
import re
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://papan2222.github.io"
PREFIX = "/animalenglish/topics/"
SPECS = [
    ("noun","名詞","人・物・場所などの名前を表します。"),
    ("verb","動詞","動作や状態を表します。"),
    ("adjective","形容詞","名詞の性質や状態を説明します。"),
    ("adverb","副詞","動作の様子や程度などを表します。"),
    ("preposition","前置詞","位置・時間・関係を表します。"),
    ("pronoun","代名詞","名詞の代わりに使われます。"),
    ("conjunction","接続詞","語句や文を結びます。"),
    ("other","冠詞・助動詞・間投詞","冠詞、助動詞、間投詞を学びます。"),
    ("irregular","不規則動詞","過去形や過去分詞が通常の -ed の規則に従わない動詞です。"),
    ("regular","規則動詞","過去形と過去分詞を原則として -ed で作る動詞です。"),
]
def h(s):
    return html.escape(str(s), quote=True)

def generate():
    source = (ROOT/"animalenglish/index.html").read_text(encoding="utf-8")
    rows = re.findall(r'<article id="([^"]+)">([\s\S]*?)</article>', source)
    ids = [i for i, _ in rows]
    if not ids or len(ids) != len(set(ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", i) for i in ids):
        raise ValueError("Invalid vocabulary IDs")
    groups = {k: [] for k, _, _ in SPECS}
    for ident, body in rows:
        pos = html.unescape(re.search(r'<p class="word-meta">([^<]+)', body)[1]).split("／")[0].strip()
        for k, name, _ in SPECS:
            if k in ("irregular", "regular"):
                match = f">{name}<" in body
            elif k == "other":
                match = bool(re.search("冠詞|助動詞|間投詞", pos))
            elif k == "verb":
                match = "動詞" in pos and "助動詞" not in pos
            elif k == "noun":
                match = "名詞" in pos.split("・")
            else:
                match = name in pos
            if match:
                groups[k].append((ident, body))
    covered = {i for group in groups.values() for i, _ in group}
    if covered != set(ids):
        raise ValueError("Unclassified vocabulary: " + ", ".join(sorted(set(ids)-covered)))
    nav = '<nav class="topic-links" aria-label="品詞別学習">' + "".join(f'<a href="{PREFIX+k}/">{name}（{len(groups[k])}）</a>' for k,name,_ in SPECS) + '</nav>'
    def page(path, title, desc, body):
        url = BASE + path
        output = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}｜どうぶつ英単語</title><meta name="description" content="{h(desc)}"><link rel="canonical" href="{url}"><meta property="og:title" content="{h(title)}｜どうぶつ英単語"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website"><link rel="stylesheet" href="{PREFIX}style.css"></head><body><header><a href="/">ホーム</a> ／ <a href="/animalenglish/">どうぶつ英単語</a> ／ <a href="{PREFIX}">品詞別学習</a><h1>{h(title)}</h1></header><main>{body}</main></body></html>'
        out = ROOT/path.strip("/")/"index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    for k,name,desc in SPECS:
        cards, table, seen = [], [], set()
        for ident, body in groups[k]:
            card = re.sub(r'(href|src|data-audio)="(word|images|audio)/', r'\1="/animalenglish/\2/', body)
            cards.append(f'<article id="{ident}">{card}</article>')
            if k in ("regular","irregular"):
                word = html.unescape(re.search(r'<h2 lang="en">([^<]+)', body)[1])
                forms = re.findall(r'<dd lang="en">([^<]+)</dd>', body)
                if len(forms) != 4:
                    raise ValueError("Incomplete verb forms: "+ident)
                if word not in seen:
                    seen.add(word)
                    table.append(f'<tr><td><a href="/animalenglish/word/{ident}.html">{h(word)}</a></td>'+"".join(f"<td>{h(html.unescape(f))}</td>" for f in forms)+"</tr>")
        grid = '<div id="gallery">'+"".join(cards)+"</div>"
        if table:
            grid = '<div class="forms-scroll"><table><thead><tr><th>原形</th><th>過去形</th><th>過去分詞</th><th>ing形</th><th>三単現</th></tr></thead><tbody>'+"".join(table)+"</tbody></table></div>"+grid
        page(PREFIX+k+"/",f"英語の{name}一覧・イラストと例文",f"{name}を動物のイラスト、意味、発音記号、英語例文、日本語訳、音声で学習。",f'<p>{desc}</p><p class="topic-note">収録済み{len(groups[k])}作品。複数の品詞を持つ語や同じ単語の別作品を含みます。</p>{grid}<h2>ほかの品詞を学ぶ</h2>{nav}<script src="{PREFIX}audio.js"></script>')
    page(PREFIX,"英単語の品詞別学習","名詞・動詞・形容詞・副詞や不規則動詞を学ぶ。",f'<p>登録済みの{len(rows)}作品を品詞と動詞の活用で分類しています。意味、発音記号、例文、音声を確認できます。</p>{nav}<p class="topic-note">複数の品詞を持つ作品は複数の分類に掲載されます。</p>')
    print("Vocabulary collections:", len(rows), "cards,", len(groups)+1, "pages")

if __name__ == "__main__":
    generate()
