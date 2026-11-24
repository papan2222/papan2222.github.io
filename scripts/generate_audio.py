import json,re,hashlib,subprocess,tempfile
from pathlib import Path
from html.parser import HTMLParser
class Blog(HTMLParser):
    def __init__(self):
        super().__init__(); self.tag=None; self.buf=[]; self.lines=[]; self.texts=[]
    def handle_starttag(self,tag,attrs):
        c=dict(attrs).get('class','').split()
        if tag=='article': self.lines=[]
        if (tag=='p' and 'en' in c) or (tag=='strong' and 'term' in c): self.tag=tag; self.buf=[]
    def handle_data(self,data):
        if self.tag: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag==self.tag:
            t=''.join(self.buf)
            if tag=='p': self.lines.append(re.sub(r'^[^\w“‘"\x27]+','',t))
            else: self.texts.append(t)
            self.tag=None
        if tag=='article' and self.lines: self.texts.append('\n'.join(self.lines)); self.lines=[]
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    texts=[]
    for w in load('game/gallery.json'):
        texts.append(w.get('captionEn',''))
        for n in w.get('study',[]):
            m=re.match(r"^([A-Za-z][A-Za-z’' -]*?)(?:\s*～)?\s*(?:/[^/]+/\s*)?[:：]",n)
            if m: texts.append(m[1].strip())
    for w in load('pandalife/works.json'):
        lines=[]
        for t in w['text']:
            for line in t.split('\n'):
                line=re.sub(r'^.*[ぁ-んァ-ヶ一-龯々]','',line)
                line=re.sub(r'^[^A-Za-z“‘"\x27]+','',line).strip()
                if re.search(r'[A-Za-z]{2}',line) and not re.search(r'[ぁ-んァ-ヶ一-龯]',line): lines.append(line)
        texts.append('\n'.join(lines))
        texts.extend(m[1].strip() for n in w.get('study',[]) for m in re.finditer(r"(?:^|[。；;]\s*)([A-Za-z][A-Za-z’' -]*?)\s*/[^/\n]+/\s*[:：]",n))
    b=Blog(); b.feed(Path('blog/index.md').read_text(encoding='utf-8')); texts.extend(b.texts)
    texts=sorted(set(' '.join(t.split()) for t in texts if t.strip()))
    out=Path('audio').resolve(); index=load(out/'index.json')
    jobs=[]
    for t in texts:
        f=index.get(t,hashlib.sha256(t.encode()).hexdigest()[:32]+'.wav')
        if not (out/f).is_file() or (out/f).stat().st_size<100: jobs.append({'text':t,'path':str(out/f)})
        index[t]=f
    print(f'New audio: {len(jobs)}',flush=True)
    if not jobs: return
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp); (p/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False),encoding='utf-8-sig')
        (p/'generate.ps1').write_text('''param($jobsPath)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$s=New-Object System.Speech.Synthesis.SpeechSynthesizer
$v=$s.GetInstalledVoices() | Where-Object {$_.Enabled -and $_.VoiceInfo.Culture.Name -eq 'en-US'} | Select-Object -First 1
if(-not $v){throw 'English voice not installed'}
$s.SelectVoice($v.VoiceInfo.Name)
$jobs=Get-Content -Raw -Encoding UTF8 $jobsPath | ConvertFrom-Json
foreach($j in $jobs){$temp=$j.path+'.tmp'; $s.SetOutputToWaveFile($temp); $s.Speak($j.text); $s.SetOutputToNull(); Move-Item -Force $temp $j.path}
$s.Dispose()
''',encoding='utf-8-sig')
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(p/'generate.ps1'),str(p/'jobs.json')],check=True)
    (out/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
