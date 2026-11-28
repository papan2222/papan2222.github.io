"""Add visible breadcrumbs and JSON-LD to canonical static pages."""
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parent
BASE="https://papan2222.github.io"
NAMES={"quotes":"パンダの英語名言","animalenglish":"どうぶつ英単語","blog":"パンダの笑える英語日記","senryu":"パンダの英語川柳","pandalife":"パンダの詩と小さな物語","game":"パンダのゲーム世界"}
MARK=re.compile(r'<!-- seo-structured:start -->[\s\S]*?<!-- seo-structured:end -->')
CRUMB=re.compile(r'<!-- seo-breadcrumb:start -->[\s\S]*?<!-- seo-breadcrumb:end -->')
def clean(s):
    return html.unescape(re.sub(r"<[^>]*>","",s)).strip()
def h(s):
    return html.escape(s,quote=True)
def main():
    ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls=[n.text for n in ET.parse(ROOT/"sitemap.xml").findall("s:url/s:loc",ns)]
    count=0
    for url in urls:
        path=unquote(urlsplit(url).path)
        parts=path.strip("/").split("/")
        if len(parts)<2 or parts[0] not in NAMES:
            continue
        target=ROOT/path.strip("/")
        if path.endswith("/"):
            target=target/"index.html"
        if not target.is_file() or target.suffix!=".html":
            continue
        source=target.read_text(encoding="utf-8")
        source=MARK.sub("",source)
        source=CRUMB.sub("",source)
        title=re.search(r"<title>([\s\S]*?)</title>",source,re.I)
        if not title or "</head>" not in source or not re.search(r"<body[^>]*>",source):
            continue
        title=clean(title[1])
        current=title.split("｜")[0].split(" | ")[0]
        crumbs=[("ホーム",BASE+"/"),(NAMES[parts[0]],BASE+"/"+parts[0]+"/")]
        middle={"authors":"作者別特集","topics":"品詞別学習"}
        if len(parts)>2 and parts[1] in middle:
            crumbs.append((middle[parts[1]],BASE+"/"+parts[0]+"/"+parts[1]+"/"))
        if len(parts)>2 and parts[0]=="quotes" and parts[1]=="works":
            author=re.search(r'<a href="(/quotes/authors/[^"]+/)">([^<]+)</a>',source)
            if author:
                crumbs.append((clean(author[2]),BASE+author[1]))
        crumbs.append((current,url))
        items=[{"@type":"ListItem","position":i,"name":name,"item":link} for i,(name,link) in enumerate(crumbs,1)]
        webpage={"@type":"WebPage","@id":url+"#page","url":url,"name":title,"inLanguage":"ja","isPartOf":{"@type":"WebSite","@id":BASE+"/#website","url":BASE+"/","name":"パンダと楽しく英語学習"},"breadcrumb":{"@id":url+"#breadcrumb"}}
        desc=re.search(r'<meta name="description" content="([^"]*)"',source)
        if desc:
            webpage["description"]=html.unescape(desc[1])
        if parts[0]=="animalenglish" and parts[1]=="word":
            webpage["@type"]=["WebPage","LearningResource"]
            webpage["learningResourceType"]="語彙学習"
        data={"@context":"https://schema.org","@graph":[webpage,{"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":items}]}
        payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
        block='<!-- seo-structured:start --><script type="application/ld+json">'+payload+'</script><style>.seo-breadcrumb{display:block;max-width:900px;margin:10px auto;padding:0 12px;font:12px/1.7 system-ui,sans-serif;overflow-wrap:anywhere}.seo-breadcrumb ol{display:flex;flex-wrap:wrap;gap:5px;list-style:none;padding:0;margin:0}.seo-breadcrumb li+li:before{content:"›";margin-right:5px;opacity:.7}.seo-breadcrumb a{color:inherit;text-decoration:underline}.seo-breadcrumb li[aria-current]{opacity:.85}</style><!-- seo-structured:end -->'
        visible='<!-- seo-breadcrumb:start --><nav class="seo-breadcrumb" aria-label="パンくずリスト"><ol>'+''.join(f'<li><a href="{h(link)}">{h(name)}</a></li>' for name,link in crumbs[:-1])+f'<li aria-current="page">{h(current)}</li></ol></nav><!-- seo-breadcrumb:end -->'
        source=source.replace("</head>",block+"</head>",1)
        source=re.sub(r"<body[^>]*>",lambda m:m[0]+visible,source,count=1)
        target.write_text(source,encoding="utf-8")
        count+=1
    print("Structured pages:",count)
if __name__=="__main__":
    main()
