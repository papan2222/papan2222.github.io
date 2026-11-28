"""Validate sitemap coverage and local targets without network requests."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
HOST = "papan2222.github.io"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

def main():
    sitemap = ET.parse(ROOT/"sitemap.xml")
    urls = [node.text for node in sitemap.findall("s:url/s:loc", NS)]
    errors = []
    if not urls:
        errors.append("Empty sitemap")
    if len(urls) != len(set(urls)):
        errors.append("Duplicate sitemap URLs")
    actual = set()
    for url in urls:
        u = urlsplit(url)
        if u.scheme != "https" or u.netloc != HOST or u.query or u.fragment:
            errors.append("Invalid canonical URL: "+url)
            continue
        path = unquote(u.path)
        actual.add(path)
        if path == "/":
            candidates = [ROOT/"index.html"]
        elif path.endswith("/"):
            rel = path.strip("/")
            candidates = [ROOT/rel/"index.html", ROOT/rel/"index.md", ROOT/(rel+".html"), ROOT/(rel+".md")]
        else:
            candidates = [ROOT/path.lstrip("/")]
        if not any(p.is_file() for p in candidates):
            errors.append("Missing sitemap target: "+path)
    expected = set()
    for q in json.loads(read("quotes.json")):
        expected.add(f'/quotes/works/{q["id"]}/')
    for w in json.loads(read("pandalife/works.json")):
        expected.add(f'/pandalife/works/{w["id"]}/')
    for w in json.loads(read("game/gallery.json")):
        expected.add(f'/game/works/{Path(w["file"]).stem}/')
    for ident in re.findall(r'<article class="work" id="([^"]+)"', read("blog/index.md")):
        expected.add(f"/blog/works/{ident}/")
    for ident in re.findall(r'id="work-([^"]+)"', read("senryu/index.md")):
        expected.add(f"/senryu/works/{ident}/")
    for link in re.findall(r'href="(word/[^"]+\.html)"', read("animalenglish/index.html")):
        expected.add("/animalenglish/"+link)
    for path in sorted(expected-actual):
        errors.append("Work missing from sitemap: "+path)
    for path in sorted(actual):
        if "/works/" not in path and "/topics/" not in path and "/authors/" not in path and not path.startswith("/animalenglish/word/"):
            continue
        target = ROOT/path.strip("/")
        if path.endswith("/"):
            target = target/"index.html"
        if not target.is_file():
            continue
        content = target.read_text(encoding="utf-8")
        canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', content)
        if not canonical or canonical[1] != "https://"+HOST+path:
            errors.append("Canonical mismatch: "+path)
    print(f"Sitemap: {len(urls)} URLs; source works: {len(expected)}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("SEO validation passed")
if __name__ == "__main__":
    main()
