import json, re, html
from pathlib import Path
root=Path('animalenglish')
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
        word=re.search(r'<h2 lang="en">(.*?)</h2>',lesson['html']).group(1)
        entries.append('<li><a href="#'+html.escape(lesson['id'],quote=True)+'">No.'+lesson['number']+' '+word+'</a></li>')
    master=root/'master.tsv'
    if master.exists():
        rows=[line.split('\t',1) for line in master.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        assert [int(n) for n,w in rows]==list(range(1,1731))
        covered={int(x['number'].split('-')[0]) for x in lessons}
        entries.extend('<li>No.'+n+' '+html.escape(w)+'（未収録）</li>' for n,w in rows if int(n) not in covered)
        entries.sort(key=lambda s:int(re.search(r'No\.(\d+)',s).group(1)))
    output=template.replace('<!-- CARDS -->',''.join(x['html'] for x in lessons)).replace('<!-- WORDLIST -->',''.join(entries))
    output=re.sub(r'(<[^>]+id="status"[^>]*>)\d+件',lambda m:m[1]+str(len(lessons))+'件',output)
    (root/'index.html').write_text(output,encoding='utf-8')
    print(f'{len(lessons)} lessons; {len(set(x["number"].split("-")[0] for x in lessons))} numbered entries')
if __name__=='__main__': main()
