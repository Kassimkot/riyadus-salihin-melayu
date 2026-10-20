# Assemble the GitHub Pages folder: app.html (content), index.html (same page for browsers), version.json, apk
import json,hashlib,shutil,sys,os
out=sys.argv[1]; base=sys.argv[2]; apk_ver=int(sys.argv[3]) if len(sys.argv)>3 else 1
os.makedirs(out,exist_ok=True)
page=open('/home/claude/app/app.html','rb').read()
ver=int(open('/home/claude/reader/VERSION').read().strip())
open(f'{out}/app.html','wb').write(page); open(f'{out}/index.html','wb').write(page)
shutil.copy('/home/claude/app/riyadus-salihin.apk',f'{out}/riyadus-salihin.apk')
shutil.copy('/home/claude/app/icon512.png',f'{out}/icon.png')
json.dump({'version':ver,'page':'app.html','sha256':hashlib.sha256(page).hexdigest(),
           'apk_version':apk_ver,'apk_sha256':hashlib.sha256(open('/home/claude/app/riyadus-salihin.apk','rb').read()).hexdigest(),'apk':base+'riyadus-salihin.apk','apk_nota':''},open(f'{out}/version.json','w'),indent=1)
open(f'{out}/.nojekyll','w').write('')
print('site ready',ver)
