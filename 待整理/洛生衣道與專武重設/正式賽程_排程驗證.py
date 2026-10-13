import json
from pathlib import Path
base=Path(__file__).parent
d=json.loads((base/'正式賽程_排程資料.json').read_text(encoding='utf8'))
ids=set(d['scores']);score=dict.fromkeys(ids,0);seen=set();opp={x:[] for x in ids}
for row in d['rounds']:
 flat=[x for a,b,w in row for x in (a,b)]
 assert len(row)==12 and set(flat)==ids and len(flat)==len(set(flat))
 for a,b,w in row:
  assert w in (a,b) and tuple(sorted((a,b))) not in seen
  seen.add(tuple(sorted((a,b))));score[w]+=1;opp[a].append(b);opp[b].append(a)
bh={x:sum(score[y] for y in opp[x]) for x in ids}
assert score==d['scores'] and bh==d['bh'] and len(seen)==48
assert score['sheng']==4 and score['lu']==3 and d['order'][7]=='lu'
assert all(bh[x]>bh['lu'] for x in ['qing','chi','feng','mu','qi','ran'])
assert max(bh[x] for x in ids-{'sheng','lu','qing','chi','feng','mu','qi','ran'} if score[x]==3)<bh['lu']
print('PASS: 24 candidates, 4 rounds, 48 distinct matches; Lu rank 8, strict qualification boundary.')
