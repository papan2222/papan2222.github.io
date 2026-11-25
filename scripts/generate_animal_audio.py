import json, subprocess, tempfile, shutil
from pathlib import Path
from html.parser import HTMLParser
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.jobs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='button' and a.get('data-audio') and a.get('data-word'):
            self.jobs.append({'text':a['data-word'],'path':str((Path('animalenglish')/a['data-audio']).resolve())})
p=Parser(); p.feed(Path('animalenglish/index.html').read_text(encoding='utf-8'))
jobs=[j for j in p.jobs if not Path(j['path']).is_file()]
Path('animalenglish/audio').mkdir(exist_ok=True)
if jobs:
    with tempfile.TemporaryDirectory() as d:
        t=Path(d); (t/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False),encoding='utf-8-sig')
        (t/'gen.ps1').write_text("""param($jobsPath)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$s=New-Object System.Speech.Synthesis.SpeechSynthesizer
$v=$s.GetInstalledVoices() | Where-Object {$_.Enabled -and $_.VoiceInfo.Culture.Name -eq 'en-US'} | Select-Object -First 1
if(-not $v){throw 'English voice not installed'}
$s.SelectVoice($v.VoiceInfo.Name)
foreach($j in (Get-Content -Raw -Encoding UTF8 $jobsPath | ConvertFrom-Json)){
 $wav=$j.path+'.wav'
 $s.SetOutputToWaveFile($wav); $s.Speak($j.text); $s.SetOutputToNull()
 & ffmpeg -nostdin -loglevel error -y -i $wav -codec:a libmp3lame -b:a 64k $j.path
 if($LASTEXITCODE -ne 0){throw 'MP3 conversion failed'}
 Remove-Item $wav
}
$s.Dispose()
""",encoding='utf-8-sig')
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(t/'gen.ps1'),str(t/'jobs.json')],check=True)
print(f'Generated {len(jobs)} MP3 files')
