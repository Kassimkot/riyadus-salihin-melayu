import re,base64,os,sys
F='/home/claude/app/fonts'
want={'fontsource-amiri-5.3.0':['400.css','700.css'],
      'fontsource-gentium-book-plus-5.3.0':['400.css','700.css','400-italic.css'],
      'fontsource-ibm-plex-sans-5.3.0':['400.css','500.css','600.css']}
subsets={'arabic','latin','latin-ext'}
faces=[]
for pkg,cssl in want.items():
    for c in cssl:
        css=open(f'{F}/{pkg}/{c}').read()
        for blk in re.findall(r'@font-face\s*\{.*?\}',css,re.S):
            m=re.search(r"url\(\./files/([^)]+\.woff2)\)",blk); sub=re.search(r'/\*\s*([\w-]+)\s*\*/',css[:css.find(blk)][-80:])
            fname=m.group(1)
            s=[x for x in subsets if f'-{x}-' in fname and not any(f'-{y}-' in fname for y in subsets if y!=x and y.startswith(x))]
            if not any(fname.split('-')[-3 if 'italic' in fname or 'normal' in fname else -2]==x or f'-{x}-' in fname for x in subsets): continue
            # keep only exact subsets
            core=re.sub(r'^(amiri|gentium-book-plus|ibm-plex-sans)-','',fname); sb=re.sub(r'-\d{3}-(normal|italic)\.woff2$','',core)
            if sb not in subsets: continue
            b64=base64.b64encode(open(f'{F}/{pkg}/files/{fname}','rb').read()).decode()
            blk=re.sub(r"src:[^;]+;",f"src: url(data:font/woff2;base64,{b64}) format('woff2');",blk)
            faces.append(blk)
style='<style>'+'\n'.join(faces)+'</style>'
src=open('/home/claude/riyadus-salihin-reader.html').read()
src=re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts\.[^"]+"[^>]*>\n?','',src)
src=src.replace('<title>','<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+style+'\n<title>',1)
src='<!-- RS_VERSION app page -->\n'+src
open('/home/claude/app/app.html','w').write(src)
print(len(faces),'faces',round(len(src)/1024),'KB', 'gfonts left:', src.count('fonts.googleapis'))
