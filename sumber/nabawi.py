import json,re
D=json.load(open('/home/claude/riyadus_salihin_ms.json')); H=json.load(open('ar_harakat.json'))
KEY=re.compile(r"(bersabda|berdoa|Baginda menjawab|Baginda bertanya|Baginda berkata|Dalam satu riwayat(?: Muslim| al-Bukhari)?:|Baginda berseru)[^\"]{0,25}$")
MS_FORCE_P={12:[2],33:[0],36:[0],44:[7],55:[0],74:[3],78:[8],91:[0],94:[0]}
MS_FORCE_NOT={21:[5,6],92:[0]}
AR_EXCL={10:[1],37:[1],88:[2],63:[0],76:[0],92:[0]}
QAWL={ # (ms substrings, ar substrings)
 19:(["Ya, ini aku.","Seseorang itu bersama orang yang dicintainya pada hari kiamat."],[]),
 21:(["Apa yang dilakukan oleh Ka'b bin Malik?","Jadilah engkau Abu Khaithamah.","Mari.","Apa yang menyebabkan engkau tertinggal? Bukankah engkau telah membeli tungganganmu?","Adapun orang ini, dia telah berkata benar. Maka bangunlah sehingga Allah memutuskan tentang dirimu.","Tidak, tetapi janganlah dia mendekatimu.","Bergembiralah dengan hari terbaik yang pernah engkau lalui sejak engkau dilahirkan oleh ibumu.","Tidak, bahkan daripada Allah 'Azza wa Jalla.","Simpanlah sebahagian hartamu, itu lebih baik bagimu."],[]),
 35:(["Jika engkau mahu, engkau bersabar dan bagimu syurga; dan jika engkau mahu, aku berdoa kepada Allah Ta'ala supaya Dia menyembuhkanmu."],[]),
 46:(["Berlindunglah dengan Allah daripada syaitan yang direjam."],[]),
 56:(["Sembahlah Allah semata-mata, dan janganlah kamu menyekutukan-Nya dengan sesuatu pun, dan tinggalkanlah apa yang dikatakan oleh nenek moyang kamu."],[]),
 92:(["kerana sesungguhnya tidak datang suatu zaman melainkan zaman selepasnya lebih buruk daripadanya, sehinggalah kamu bertemu Tuhan kamu."],["فَإِنَّهُ لَا يَأْتِي زَمَانٌ إِلَّا وَالَّذِي بَعْدَهُ شَرٌّ مِنْهُ حَتَّى تَلْقَوْا رَبَّكُمْ"]),
}
FIL={
 6:(["Rasulullah ﷺ datang menziarahiku pada tahun Haji Wada'"],["جَاءَنِي رَسُولُ اللهِ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ يَعُودُنِي عَامَ حَجَّةِ الْوَدَاعِ"]),
 21:(["Bahawa Nabi ﷺ keluar ke Perang Tabuk pada hari Khamis, dan Baginda suka keluar (bermusafir) pada hari Khamis.","Baginda tidak pulang dari perjalanan melainkan pada siang hari, pada waktu dhuha. Apabila Baginda tiba, Baginda memulakan dengan masjid, lalu bersolat dua rakaat di dalamnya, kemudian duduk di situ."],
     ["أَنَّ النَّبِيَّ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ خَرَجَ فِي غَزْوَةِ تَبُوكَ يَوْمَ الْخَمِيسِ، وَكَانَ يُحِبُّ أَنْ يَخْرُجَ يَوْمَ الْخَمِيسِ","وَكَانَ لَا يَقْدَمُ مِنْ سَفَرٍ إِلَّا نَهَارًا فِي الضُّحَى، فَإِذَا قَدِمَ بَدَأَ بِالْمَسْجِدِ فَصَلَّى فِيهِ رَكْعَتَيْنِ ثُمَّ جَلَسَ فِيهِ"]),
 22:(["Lalu Nabi Allah ﷺ memerintahkan supaya pakaiannya diikat kemas pada tubuhnya, kemudian Baginda memerintahkan supaya dia direjam","Kemudian Baginda menyembahyangkan jenazahnya."],["فَأَمَرَ بِهَا نَبِيُّ اللهِ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ فَشُدَّتْ عَلَيْهَا ثِيَابُهَا، ثُمَّ أَمَرَ بِهَا فَرُجِمَتْ، ثُمَّ صَلَّى عَلَيْهَا"]),
 26:(["*lalu Baginda memberi mereka"],["*فَأَعْطَاهُمْ"]),
 29:(["Maka berlinanglah air mata Baginda."],["فَفَاضَتْ عَيْنَاهُ"]),
 42:(["Maka berubahlah wajah Baginda sehingga menjadi merah seperti pewarna merah."],["فَتَغَيَّرَ وَجْهُهُ حَتَّى كَانَ كَالصِّرْفِ"]),
 44:(["Lalu Nabi ﷺ mengambilnya dan mengunyahnya, kemudian mengeluarkannya dari mulut Baginda dan meletakkannya ke dalam mulut bayi itu. Kemudian Baginda mentahnikkannya dan menamakannya Abdullah."],["فَأَخَذَهَا النَّبِيُّ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ فَمَضَغَهَا، ثُمَّ أَخَذَهَا مِنْ فِيهِ فَجَعَلَهَا فِي فِي الصَّبِيِّ، ثُمَّ حَنَّكَهُ وَسَمَّاهُ عَبْدَ اللهِ"]),
 53:(["menunggu sehingga apabila matahari tergelincir, Baginda berdiri di hadapan mereka"],["انْتَظَرَ حَتَّى إِذَا مَالَتِ الشَّمْسُ قَامَ فِيهِمْ"]),
 78:(["Baginda tidak menghukumnya, lalu duduk.","Rasulullah ﷺ mengambil pedang itu","Maka Baginda melepaskannya."],["وَلَمْ يُعَاقِبْهُ وَجَلَسَ","فَأَخَذَ رَسُولُ اللهِ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ السَّيْفَ","فَخَلَّى سَبِيلَهُ"]),
 88:(["Baginda memberi salam, kemudian bangun dengan tergesa-gesa, melangkahi bahu orang ramai menuju ke salah sebuah bilik isteri-isterinya."],["فَسَلَّمَ ثُمَّ قَامَ مُسْرِعًا، فَتَخَطَّى رِقَابَ النَّاسِ إِلَى بَعْضِ حُجَرِ نِسَائِهِ"]),
 91:(["Rasulullah ﷺ mengambil sebilah pedang pada hari Perang Uhud"],["أَخَذَ سَيْفًا يَوْمَ أُحُدٍ"]),
 94:(["Lalu Rasulullah ﷺ memanggil Ali bin Abi Talib رضي الله عنه dan memberikan panji itu kepadanya"],["فَدَعَا رَسُولُ اللهِ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ عَلِيَّ بْنَ أَبِي طَالِبٍ رَضِيَ اللهُ عَنْهُ فَأَعْطَاهُ إِيَّاهَا"]),
}
def ms_quotes(t):
    out=[];i=0
    while True:
        s=t.find('"',i)
        if s<0: break
        e=t.find('"',s+1)
        if e<0: break
        out.append((s,e+1)); i=e+1
    return out
def find_all(t,sub):
    every=sub.startswith('*'); sub=sub.lstrip('*'); res=[]; i=t.find(sub)
    assert i>=0,(sub[:50])
    while i>=0:
        res.append((i,i+len(sub)))
        if not every: break
        i=t.find(sub,i+len(sub))
    return res
for h in D['hadith']:
    n=h['no']; t=h['ms']; a=H[str(n)]; ms=[]; ar=[]
    for k,(s,e) in enumerate(ms_quotes(t)):
        p=bool(KEY.search(t[max(0,s-45):s]))
        if k in MS_FORCE_P.get(n,[]): p=True
        if k in MS_FORCE_NOT.get(n,[]): p=False
        if p: ms.append([s+1,e-1,'q'])
    for k,m in enumerate(re.finditer(r'«([^»]*)»',a)):
        if k in AR_EXCL.get(n,[]): continue
        ar.append([m.start(1),m.end(1),'q'])
    for src,kind in ((QAWL,'q'),(FIL,'f')):
        if n in src:
            for sub in src[n][0]: ms+= [[s,e,kind] for s,e in find_all(t,sub)]
            for sub in src[n][1]: ar+= [[s,e,kind] for s,e in find_all(a,sub)]
    for L in (ms,ar):
        L.sort()
        for x,y in zip(L,L[1:]): assert x[1]<=y[0],(n,x,y)
    h['nabawi']={'ms':ms,'ar':ar}
json.dump(D,open('/home/claude/riyadus_salihin_ms.json','w'),ensure_ascii=False,indent=2)
miss=[h['no'] for h in D['hadith'] if not h['nabawi']['ms']]; missa=[h['no'] for h in D['hadith'] if not h['nabawi']['ar']]
print('no ms marks:',miss,' no ar marks:',missa)
