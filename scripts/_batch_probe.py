# -*- coding: utf-8 -*-
"""临时探针：统计第001-003章带值（只读，不改动任何正文）。"""
import re, statistics, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
FEAR = ['血', '死', '鬼', '尸', '怕', '惊', '惨', '恐']

for f in ['validation/十九层/第001章-十九层.md',
          'validation/十九层/第002章-门牌.md',
          'validation/十九层/第003章-上行.md']:
    t = open(f, encoding='utf-8').read()
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    n = len(re.sub(r'\s', '', body))
    paras = [p.strip() for p in re.split(r'\n+', body) if p.strip()]
    lens = [len(re.sub(r'\s', '', p)) for p in paras]
    dlg_straight = sum(1 for p in paras if p.startswith('"') or p.startswith('“'))
    dlg_curly = sum(1 for p in paras if p.startswith('“'))
    dlg_ascii = sum(1 for p in paras if p.startswith('"'))
    run = maxrun = 0
    for p in paras:
        if p.startswith('“') or p.startswith('"'):
            run += 1
            maxrun = max(maxrun, run)
        else:
            run = 0
    print('==', f)
    print('  n=%d paras=%d avg=%.1f single%%=%.1f dlg_curly=%d dlg_ascii=%d dlg%%=%.1f maxrun=%d'
          % (n, len(paras), statistics.mean(lens),
             sum(1 for l in lens if l <= 10) / len(lens) * 100,
             dlg_curly, dlg_ascii, dlg_straight / len(paras) * 100, maxrun))
    print('  ellipsis=%d  bang=%d  dash=%d  fear=%d  gui=%d'
          % (body.count('……'), body.count('！'), body.count('——'),
             sum(body.count(w) for w in FEAR), body.count('鬼')))
    print('  fear per 1000 = %.2f' % (sum(body.count(w) for w in FEAR) / max(n / 1000, 0.5)))
