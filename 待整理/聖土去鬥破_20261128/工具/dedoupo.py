# -*- coding: utf-8 -*-
"""聖土去鬥破：有序替換。用法：python -I dedoupo.py ROOT [--write] [--report OUT]"""
import io, os, re, sys, collections

ROOT = sys.argv[1]
WRITE = '--write' in sys.argv
REPORT = sys.argv[sys.argv.index('--report')+1] if '--report' in sys.argv else None
DIRS = ['設定', '大綱', 'AI團隊']
SKIP_PARTS = ('歸檔', '待整理', '.claude', '決策', '正文')

R = {'鬥者':'點塘','鬥師':'披紗','大鬥師':'著甲','鬥靈':'留形','鬥王':'展翼',
     '鬥皇':'實翼','鬥宗':'張廓','鬥尊':'起穹'}
stage = '大鬥師|鬥者|鬥師|鬥靈|鬥王|鬥皇|鬥宗|鬥尊'

RULES = [
  # 複合詞
  (r'鬥氣化翼', '展翼'), (r'鬥氣紗衣', '紗'), (r'鬥氣鎧甲', '甲'), (r'鬥氣鎧', '甲'),
  (r'鬥氣凝物', '留形'), (r'鬥氣修士', '聖土修士'), (r'鬥尊兵器', '穹兵'),
  (r'異火之地', '火地'), (r'煉藥師公會', '蒸瓶公會'), (r'鬥技場', '火坪'),
  # 小階
  (r'(%s)([一二三四五六七八九])星' % stage, lambda m: R[m.group(1)] + m.group(2) + '分'),
  (r'(%s)巔峰' % stage, lambda m: R[m.group(1)] + '長滿'),
  (r'鬥聖初期', '初根'), (r'鬥聖中期', '中根'), (r'鬥聖後期', '深根'), (r'鬥聖巔峰', '根滿'),
  (r'鬥聖([一二三四五六七八九])星', r'落根\1分'),
  (r'鬥之氣([一二三四五六七八九])段', r'白身\1段'),
  # 單詞（長詞先）
  (r'大鬥師', '著甲'), (r'鬥之氣', '白身'), (r'鬥者', '點塘'), (r'鬥師', '披紗'),
  (r'鬥靈', '留形'), (r'鬥王', '展翼'), (r'鬥皇', '實翼'), (r'鬥宗', '張廓'), (r'鬥尊', '起穹'),
  (r'半聖', '垂根'), (r'末代鬥帝', '末代帝'), (r'(位|名|歷代|五|四|三|兩|二|一)鬥帝', r'\1帝'), (r'(位|名)鬥聖', r'\1聖'), (r'鬥聖', '落根'), (r'鬥帝', '戴天'),
  (r'化翼', '展翼'), (r'氣旋', '火塘'), (r'鬥晶', '塘晶'), (r'(?<!戰)鬥技', '戰技'), (r'鬥氣', '身火'),
  (r'煉藥師', '丹匠'), (r'魔核', '獸核'), (r'魔獸', '核獸'), (r'納戒', '廓匣'),
  (r'(?<![化])靈境', '明境'), (r'(?<![洞])天境', '穹境'),
]
RULES = [(re.compile(p), r) for p, r in RULES]

per_file = {}
per_rule = collections.Counter()
for d in DIRS:
    for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
        if any(s in dp.replace('\\', '/').split('/') for s in SKIP_PARTS):
            continue
        for f in fn:
            if not f.endswith('.md'):
                continue
            p = os.path.join(dp, f)
            s = io.open(p, encoding='utf-8').read()
            parts = re.split(r'(\]\([^)]*\))', s)
            n = 0
            for i in range(0, len(parts), 2):
                seg = parts[i]
                for rx, rep in RULES:
                    seg, k = rx.subn(rep, seg)
                    if k:
                        per_rule[rx.pattern] += k; n += k
                parts[i] = seg
            t = ''.join(parts)
            if n:
                per_file[os.path.relpath(p, ROOT)] = n
                if WRITE:
                    io.open(p, 'w', encoding='utf-8', newline='').write(t)

out = ['files=%d total=%d' % (len(per_file), sum(per_file.values()))]
out += ['%6d  %s' % (v, k) for k, v in per_rule.most_common()]
out += ['', '# per file'] + ['%5d  %s' % (v, k) for k, v in sorted(per_file.items(), key=lambda x: -x[1])]
txt = '\n'.join(out)
if REPORT:
    io.open(REPORT, 'w', encoding='utf-8').write(txt)
print('\n'.join(out[:50]))
