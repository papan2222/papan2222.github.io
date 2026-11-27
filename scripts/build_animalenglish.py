import json, re, html
from pathlib import Path
root=Path('animalenglish')
def individual(lesson, template):
    ident=lesson['id']
    assert re.fullmatch(r'[a-zA-Z0-9_-]+',ident)
    card=lesson['html'].replace('src="images/','src="../images/').replace('data-audio="audio/','data-audio="../audio/')
    word=re.search(r'<h2 lang="en">(.*?)</h2>',card).group(1)
    meaning=re.search(r'<p class="meaning">(.*?)</p>',card)
    desc=html.escape(html.unescape(word+'：'+(meaning.group(1) if meaning else '')+'｜どうぶつ英単語'),quote=True)
    url='https://papan2222.github.io/animalenglish/word/'+ident+'.html'
    img=re.search(r'src="\.\./images/([^"]+)"',card).group(1)
    css=template.split('<style>',1)[1].split('</style>',1)[0]
    script=template.split('const player=new Audio();',1)[1].split('</script>',1)[0]
    page='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+desc+'</title><meta name="description" content="'+desc+'"><link rel="canonical" href="'+url+'"><meta property="og:title" content="'+desc+'"><meta property="og:image" content="https://papan2222.github.io/animalenglish/images/'+img+'"><meta property="og:url" content="'+url+'"><meta name="twitter:card" content="summary_large_image"><style>'+css+'main{max-width:560px}</style></head><body><header><a href="../">英単語一覧へ戻る</a></header><main><div id="gallery">'+card+'</div><p><a href="../">英単語一覧へ戻る</a></p></main><script>const g=document.getElementById("gallery");const player=new Audio();'+script+'</script></body></html>'
    dest=root/'word'
    dest.mkdir(exist_ok=True)
    (dest/(ident+'.html')).write_text(page,encoding='utf-8')

def linked_card(lesson):
    url='word/'+lesson['id']+'.html'
    return re.sub(r'(<img\b[^>]*>)',lambda m:'<a href="'+url+'" aria-label="作品の個別ページ">'+m[1]+'</a>',lesson['html'],count=1).replace('</h2>','</h2><p><a href="'+url+'">個別ページ・投稿用リンク</a></p>',1)

def main():
    lessons=json.loads((root/'lessons.json').read_text(encoding='utf-8'))
    template=(root/'template.html').read_text(encoding='utf-8')
    assert template.count('<!-- CARDS -->')==1 and template.count('<!-- WORDLIST -->')==1
    ids=set()
    for lesson in lessons:
        assert lesson['id'] not in ids, lesson['id']
        ids.add(lesson['id'])
        assert re.fullmatch(r'[0-9]+(?:-[0-9]+)?',lesson['number'])
        assert 1<=int(lesson['number'].split('-')[0])<=1730
        assert '<article id="'+lesson['id']+'">' in lesson['html']
    lessons.sort(key=lambda x:tuple(map(int,x['number'].split('-'))))
    entries=[]
    for lesson in lessons:
        individual(lesson, template)
    for lesson in lessons:
        word=re.search(r'<h2 lang="en">(.*?)</h2>',lesson['html']).group(1)
        entries.append('<li><a href="word/'+html.escape(lesson['id'],quote=True)+'.html">No.'+lesson['number']+' '+word+'</a></li>')
    master=root/'master.tsv'
    if master.exists():
        rows=[line.split('\t',1) for line in master.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        assert [int(n) for n,w in rows]==list(range(1,1731))
        covered={int(x['number'].split('-')[0]) for x in lessons}
        entries.extend('<li>No.'+n+' '+html.escape(w)+'（未収録）</li>' for n,w in rows if int(n) not in covered)
        entries.sort(key=lambda s:int(re.search(r'No\.(\d+)',s).group(1)))
    output=template.replace('<!-- CARDS -->',''.join(linked_card(x) for x in lessons)).replace('<!-- WORDLIST -->',''.join(entries))
    output=re.sub(r'(<[^>]+id="status"[^>]*>)\d+件',lambda m:m[1]+str(len(lessons))+'件',output)
    (root/'index.html').write_text(output,encoding='utf-8')
    print(f'{len(lessons)} lessons; {len(set(x["number"].split("-")[0] for x in lessons))} numbered entries')
if __name__=='__main__': main()
