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
HON=[('رضي الله عنه وعنها',None),('رضي الله عنهما','﵄'),('رضي الله عنهم','﵃'),('رضي الله عنهن','﵅'),('رضي الله عنها','﵂'),('رضي الله عنه','﵁'),
     ('عليهم السلام','﵈'),('عليها السلام','﵍'),('عليه السلام','﵇'),('رحمهم الله','﵏'),('رحمه الله','﵀')]
def honor(t, spans=None):
    # replace honorific phrases with single glyphs; remap [start,end) offsets that point into t
    if not t: return t
    out=[];i=0;pos=[]  # pos[i] = index in output where input char i lands
    while i<len(t):
        for k,v in HON:
            if t.startswith(k,i) and not (i+len(k)<len(t) and '\u0621'<=t[i+len(k)]<='\u064A'):
                rep=v if v else k
                for j in range(len(k)): pos.append(len(out) if v else len(out)+j)
                out.extend(rep); i+=len(k); break
        else:
            pos.append(len(out)); out.append(t[i]); i+=1
    pos.append(len(out))
    if spans is not None:
        for sp in spans: sp[0]=pos[sp[0]]; sp[1]=pos[sp[1]]
    return ''.join(out)
import copy
for x in H:
    if x.get('nabawi'): x['nabawi']=copy.deepcopy(x['nabawi'])
    x['ms']=honor(x['ms'], (x.get('nabawi') or {}).get('ms'))
    for f in ('takhrij','catatan','catatan_penterjemah'):
        if x.get(f): x[f]=honor(x[f])
for e in d.get('bab_kosong',[]):
    for f in ('penutup_ms',):
        if e.get(f): e[f]=honor(e[f])
data={'total':1896,'hadith':H,'bab_kosong':d.get('bab_kosong',[])}
import time
VER=time.strftime('%Y%m%d%H%M', time.gmtime(time.time()+8*3600))
s=open('template.html').read().replace('__VERSION__',VER).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
open('/home/claude/riyadus-salihin-reader.html','w').write(s)
open('/home/claude/reader/VERSION','w').write(VER)
print(len(s),VER)
