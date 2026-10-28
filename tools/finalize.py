import json,os,hashlib,datetime
HERE=os.path.dirname(os.path.abspath(__file__))
CONTENT=os.path.join(HERE,'..','app','content')
RAW=os.path.join(HERE,'raw')
study=json.load(open(os.path.join(HERE,'study.json')))
meta=json.load(open(os.path.join(HERE,'library.json')))
order=meta['order']
cat={"version":1,"updated":datetime.date.today().isoformat(),"packs":[]}
for pid in order:
    p=json.load(open(f'{RAW}/{pid}.json'))
    p['study']=study.get(pid,[])
    for sc in p['study']:
        for i,l in enumerate(sc['lines']): l['audio']=f"audio/{pid}/{sc['id']}-{i}.mp3"
    s=json.dumps(p,ensure_ascii=False,separators=(',',':'))
    open(f'{CONTENT}/packs/{pid}.json','w').write(s)
    nsp=sum(1 for a in p['acts'] for x in a['scenes'] for it in x['items'] if it[0]=='s')
    cat['packs'].append({k:p[k] for k in ['id','title','titleZh','author','authorZh','year','kind','level','blurb']}|
        {"file":f"packs/{pid}.json","rev":hashlib.sha1(s.encode()).hexdigest()[:8],"speeches":nsp,
         "studyScenes":[{"id":x['id'],"titleZh":x['titleZh']} for x in p['study']]})
json.dump(cat,open(f'{CONTENT}/catalog.json','w'),ensure_ascii=False,indent=1)
print('catalog:',[p['id'] for p in cat['packs']])
