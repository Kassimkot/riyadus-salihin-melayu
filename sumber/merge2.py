import json,re,sys
QFILE='quran_b2.json'
Q=json.load(open(QFILE)) if len(sys.argv)>1 else {}
D=json.load(open('/home/claude/riyadus_salihin_ms.json')); H=json.load(open('ar_harakat.json'))
files=['b_095_111.json','b_112_141.json','b_142_155.json','b_156_176.json']
new=[]; [new.extend(json.load(open(f))) for f in files]
assert [h['no'] for h in new]==list(range(95,177)), [h['no'] for h in new][:5]
def strip_marks(t):
    out=[];spans=[];stack=[]
    for ch in t:
        if ch in '⟦⟪': stack.append((len(''.join(out)) if False else sum(len(x) for x in out), 'q' if ch=='⟦' else 'f'))
        elif ch in '⟧⟫':
            s,k=stack.pop(); assert (k=='q')==(ch=='⟧'),'mismatch'; spans.append([s,sum(len(x) for x in out),k])
        else: out.append(ch)
    assert not stack,'unclosed'
    return ''.join(out),sorted(spans)
def fillq(t,ar):
    def rep(m):
        k=m.group(1)
        if k not in Q: return m.group(0)
        return ('﴿'+Q[k]+'﴾') if ar else ('{'+Q[k]+'}')
    return re.sub(r'﴿(Q[0-9_a-d]+)﴾',rep,t) if ar else re.sub(r'\{(Q[0-9_a-d]+)\}',rep,t)
strip=lambda s: re.sub(r'[ً-ْٰ]','',s)
problems=[]
for h in new:
    ms,msp=strip_marks(fillq(h['ms'],False)); ar,arp=strip_marks(fillq(h.pop('ar'),True))
    h['ms']=ms; H[str(h['no'])]=ar; h['nabawi']={'ms':msp,'ar':arp}
    if 'SAW' in ms or re.search(r'\bRA\b',ms): problems.append((h['no'],'latin SAW/RA'))
    a=re.findall(r'رضي الله (عن\w+)',strip(ar)); m=re.findall(r'رضي الله (عن\w+)',ms+' '+h['takhrij'])
    if a!=m: problems.append((h['no'],'RA',a,m))
    if not msp or not arp: problems.append((h['no'],'no nabawi',len(msp),len(arp)))
    L=len(re.findall(r'[ء-ي]',ar)); M=len(re.findall(r'[ً-ْ]',ar))
    if M/L<0.6: problems.append((h['no'],'low harakat',round(M/L,2)))
    left=re.findall(r'Q\d+_\w*',ms+ar)
    if left: problems.append((h['no'],'quran placeholder',left))
for p in problems: print(p)
if len(sys.argv)>1 and not any(p[1]=='quran placeholder' for p in problems):
    D['hadith']=[h for h in D['hadith'] if h['no']<95]+new
    D['kemajuan']='Hadis 1–176 daripada 1896 (Bab 1–20)'
    json.dump(D,open('/home/claude/riyadus_salihin_ms.json','w'),ensure_ascii=False,indent=2)
    json.dump(dict(sorted(H.items(),key=lambda x:int(x[0]))),open('ar_harakat.json','w'),ensure_ascii=False,indent=0)
    print('MERGED',len(D['hadith']))
