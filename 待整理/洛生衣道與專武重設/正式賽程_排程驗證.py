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
# D157 (2026-10-17): R3 lu beats chi. Lu 4 wins bh6 first, sheng 4 bh5 second, n12 3 bh6 eighth, chi 2 out.
o=d['order'];assert sorted(o)==sorted(ids)
assert all((score[o[i]],bh[o[i]])>=(score[o[i+1]],bh[o[i+1]]) for i in range(len(o)-1))
assert score['lu']==4 and score['sheng']==4 and bh['lu']>bh['sheng'] and o[:2]==['lu','sheng']
assert o[7]=='n12' and score['chi']==2 and 'chi' not in o[:8]
assert (score['n12'],bh['n12'])>max((score[x],bh[x]) for x in o[8:])
print('PASS: 24 candidates, 4 rounds, 48 distinct matches; Lu rank 1, Sheng 2, n12 rank 8, Chi out; strict qualification boundary.')
