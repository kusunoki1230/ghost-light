import json,sys
pid,q,n=sys.argv[1],sys.argv[2],int(sys.argv[3])
p=json.load(open(f'raw/{pid}.json'))
for ai,a in enumerate(p['acts']):
  for si,s in enumerate(a['scenes']):
    for ii,it in enumerate(s['items']):
      if it[0]=='s' and any(q in l for l in it[2]):
        print(ai,si,ii,s['title'])
        for j in s['items'][ii:ii+n]: print('  ',j)
        sys.exit()
