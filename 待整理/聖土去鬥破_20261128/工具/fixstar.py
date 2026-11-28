# -*- coding: utf-8 -*-
import io, os, re, sys, collections
ROOT = sys.argv[1]
PH = {'初期': '初根', '中期': '中根', '後期': '深根'}
RX = [
    (re.compile(r'(初根|中根|深根)([一二三四五六七八九])星'), r'\1\2分'),
    (re.compile(r'(初期|中期|後期)([一二三四五六七八九])星'), lambda m: PH[m.group(1)] + m.group(2) + '分'),
    (re.compile(r'(初期|中期|後期)落根'), lambda m: PH[m.group(1)] + '落根'),
    (re.compile(r'(白身|點塘|披紗|著甲|留形|展翼|實翼|張廓|起穹|垂根|落根)([一二三四五六七八九])星'), r'\1\2分'),
]
cnt = collections.Counter(); files = 0
for d in ['設定', '大綱', 'AI團隊']:
    for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
        for f in fn:
            if not f.endswith('.md'):
                continue
            p = os.path.join(dp, f)
            s = io.open(p, encoding='utf-8').read()
            parts = re.split(r'(\]\([^)]*\))', s); n = 0
            for i in range(0, len(parts), 2):
                for r, rep in RX:
                    parts[i], k = r.subn(rep, parts[i]); cnt[r.pattern] += k; n += k
            t = ''.join(parts).replace('#末代鬥帝定', '#末代帝定')
            if t != s:
                files += 1
                io.open(p, 'w', encoding='utf-8', newline='').write(t)
print(files, sum(cnt.values()))
