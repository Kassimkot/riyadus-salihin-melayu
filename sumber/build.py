import json,re,sys
d=json.load(open('/home/claude/riyadus_salihin_ms.json'))
A=json.load(open('/tmp/claude-0/-home-claude/3449f8d8-f394-5417-95f1-c258b1d53b6e/scratchpad/dl/ordered.json'))
def clean(t):
    t=re.sub(r'[‎‏‍‪-‮]','',t)
    t=re.sub(r'[ \t]+',' ',t)
    t=re.sub(r' *\n *','\n',t)
    t=re.sub(r'\n{2,}','\n',t)
    return t.strip()
HK=json.load(open('ar_harakat.json'))
H=[]
for h in d['hadith']:
    x=dict(h); x['ar']=HK.get(str(h['no'])) or clean(A[h['no']-1]['arabic']); x['baris']=str(h['no']) in HK; H.append(x)
data={'total':1896,'hadith':H,'bab_kosong':d.get('bab_kosong',[])}
import time
VER=time.strftime('%Y%m%d%H%M', time.gmtime(time.time()+8*3600))
s=open('template.html').read().replace('__VERSION__',VER).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
open('/home/claude/riyadus-salihin-reader.html','w').write(s)
open('/home/claude/reader/VERSION','w').write(VER)
print(len(s),VER)
