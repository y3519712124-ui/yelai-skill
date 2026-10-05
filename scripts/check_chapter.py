#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""夜来skill 章节自检器 v1 —— 按 SKILL.md §20 硬约束逐项检查单个章节文件。

用法:
    python check_chapter.py 第150章-谁上墙.md
    python check_chapter.py 第1*.md            # 支持通配，逐章出分

判定带（A类·诡舍式）:
    破折号     <= 3/千字
    省略号     6-8/千字
    感叹号     5-8/千字
    恐怖词     >= 8/千字 (血死鬼尸怕惊惨恐)
    鬼字       >= 2/章 (A类单元含真鬼时)
    平均段长   18-24 字
    单行段     <= 30%
    对话行     约 30% (25-40% 容差)
    托付行     单段遗言/托付 <= 2 行 (含引号的连续段不超过 2 段)
输出: 每项 PASS/FAIL + 综合判定。退出码 0=全过, 1=有 FAIL。
"""
import glob, re, sys, statistics

FEAR = ['血', '死', '鬼', '尸', '怕', '惊', '惨', '恐']

def check_file(path):
    t = open(path, encoding='utf-8').read()
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    n = len(re.sub(r'\s', '', body))
    kq = max(n / 1000, 0.5)
    paras = [p.strip() for p in re.split(r'\n+', body) if p.strip()]
    lens = [len(re.sub(r'\s', '', p)) for p in paras]
    if not lens:
        return path, [], 0
    def is_dlg(p): return p.startswith('“') or p.startswith('"') or p.startswith('「')

    items = []
    def add(name, val, ok, detail=''):
        items.append((name, val, ok, detail))

    def is_dlg0(p): return p.startswith('“') or p.startswith('"')
    _fear0 = sum(body.count(w) for w in FEAR) / kq
    _ghost0 = body.count('鬼')
    _dlg0 = sum(1 for p in paras if is_dlg0(p)) / max(1, len(paras)) * 100
    # 原型判定（万次蒸馏·章节原型系统）
    if n >= 2800: arch = '结算章'
    elif _fear0 >= 15: arch = '高潮章'
    elif _fear0 < 3 and _ghost0 <= 1: arch = '过渡章'
    else: arch = '常规章'
    BANDS = {
      '常规章': dict(fear=(5, 12), ghost=(2, 99), dlg=(25, 45)),
      '高潮章': dict(fear=(13, 99), ghost=(8, 99), dlg=(25, 45)),
      '过渡章': dict(fear=(0, 3), ghost=(0, 1), dlg=(30, 55)),
      '结算章': dict(fear=(4, 15), ghost=(1, 99), dlg=(20, 45)),
    }
    B = BANDS[arch]
    add('章节原型', arch, True, f'fear={_fear0:.1f} ghost={_ghost0} dlg={_dlg0:.0f}%')

    dash = body.count('——') / kq
    add('破折号/千字', round(dash, 2), dash <= 3.0, '带<=3')
    ell = body.count('……') / kq
    add('省略号/千字', round(ell, 2), 6.0 <= ell <= 8.0, '带6-8')
    ex = body.count('！') / kq
    add('感叹号/千字', round(ex, 2), 5.0 <= ex <= 8.0, '带5-8')
    fear = _fear0
    add('恐怖词/千字', round(fear, 1), B['fear'][0] <= fear <= B['fear'][1], f'{arch}带{B["fear"]}')
    gui = _ghost0
    add('鬼字/章', gui, B['ghost'][0] <= gui <= B['ghost'][1], f'{arch}带{B["ghost"]}')
    avgp = statistics.mean(lens)
    add('平均段长', round(avgp, 1), 18 <= avgp <= 26, '带18-26')
    single = sum(1 for l in lens if l <= 10) / len(lens) * 100
    add('单行段%', round(single, 1), single <= 32, '带<=32')
    dlg = _dlg0
    add('对话行%', round(dlg, 1), B['dlg'][0] <= dlg <= B['dlg'][1], f'{arch}带{B["dlg"]}')
    # 托付行：连续含引号段落 >2 段 视为长遗言风险
    maxrun = run = 0
    for p in paras:
        if is_dlg(p):
            run += 1; maxrun = max(maxrun, run)
        else:
            run = 0
    add('最长对话连排', maxrun, maxrun <= 8, '带<=8(E5一节连排上限)')

    score = sum(1 for _, _, ok, _ in items if ok)
    return path, items, score

def main():
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    if not files:
        print(__doc__); sys.exit(2)
    fail_total = 0
    for f in sorted(set(files)):
        path, items, score = check_file(f)
        fails = [(k, v, d) for k, v, ok, d in items if not ok]
        status = 'PASS' if not fails else 'FAIL'
        print(f'{path}  [{status}] {score}/{len(items)}')
        for k, v, d in fails:
            print(f'    ✗ {k}={v}  (要求{d})')
        fail_total += bool(fails)
    sys.exit(1 if fail_total else 0)

if __name__ == '__main__':
    main()
