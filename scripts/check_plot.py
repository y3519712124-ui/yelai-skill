#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""夜来skill 情节体检器 v1 —— 单元/章级"节拍审计"，对原作1001章实测带值。

对标数据来源：《诡舍》全本1001章矩阵（_诡舍-1001章矩阵.json，2026-10-05 复算）
    章尾类型全本占比:  陈述31.7% / 对话30.5% / 惊叹25.3% / 省略11.9% / 问句0.7%
    四大原型:          常规77.1% / 高潮13.3% / 过渡6.9% / 结算2.7%
    恐怖词带:          常规8.3 / 高潮18.8 / 过渡2.1 / 结算9.1（每千字）
    死亡节拍(死+尸):   常规4.5 / 高潮8.4 / 过渡1.4 / 结算10.0（每章）
    单元节拍模板:      过渡(1-2) → 常规×N → 首死 → 常规×N → 高潮×2-4 → 结算(1)
    结算章:            ≥2800字(2.4倍长)，有恐怖复盘（fear≥4，死亡节拍在）

用法:
    python check_plot.py 目录/第0*.md
    python check_plot.py 目录/第0*.md --units "1-14:理发店,15-33:账房间章,34-50:旅馆,51-60:归安镇"
输出: 逐章节拍表 + 单元聚合 + 五项体检（章尾/高潮/结算/死亡节拍/恐怖洼地），退出码 0=全过。
"""
import glob, re, sys, statistics
from collections import Counter

FEAR = ['血', '死', '鬼', '尸', '怕', '惊', '惨', '恐']
# 原作实测带
CORPUS = dict(etype=dict(statement=31.7, dialogue=30.5, exclaim=25.3, ellipsis=11.9, question=0.7),
              death=dict(常规=4.5, 高潮=8.4, 过渡=1.4, 结算=10.0),
              fear=dict(常规=8.3, 高潮=18.8, 过渡=2.1, 结算=9.1))

def etype_of(paras):
    """按最后一个'真实叙事段'判章尾；跳过账本/系统式【】块与独立省略号段。"""
    for p in reversed(paras):
        s = p.strip()
        if not s or s.startswith('【') or s in ('……', '…', '——'):
            continue
        if s.endswith('…'): return 'ellipsis'
        if s.endswith(('！', '!')): return 'exclaim'
        if s.endswith(('？', '?')): return 'question'
        if s.startswith('"') or s.startswith('“'): return 'dialogue'
        return 'statement'
    return 'statement'

def arch(n, fear, ghost):
    if n >= 2800: return '结算章'
    if fear >= 15: return '高潮章'
    if fear < 3 and ghost <= 1: return '过渡章'
    return '常规章'

def chapter_stats(path):
    t = open(path, encoding='utf-8').read()
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    n = len(re.sub(r'\s', '', body)); kq = max(n / 1000, .5)
    fear = sum(body.count(w) for w in FEAR) / kq
    ghost = body.count('鬼')
    death = body.count('死') + body.count('尸')
    paras = [p.strip() for p in re.split(r'\n+', body) if p.strip()]
    last = paras[-1] if paras else ''
    ch = int(re.search(r'第0*(\d+)章', path).group(1))
    return dict(ch=ch, n=n, fear=fear, ghost=ghost, death=death,
                etype=etype_of(paras), arch=arch(n, fear, ghost), path=path)

def main():
    argv = sys.argv[1:]
    units_arg = None
    if '--units' in argv:
        i = argv.index('--units'); units_arg = argv[i + 1]; del argv[i:i + 2]
    files = []
    for pat in argv: files.extend(glob.glob(pat))
    if not files: print(__doc__); sys.exit(2)
    rows = sorted((chapter_stats(f) for f in set(files)), key=lambda r: r['ch'])

    print('== 逐章节拍表 ==')
    for r in rows:
        print('第%02d章 fear%5.1f death%2d ghost%2d %-9s %s' % (r['ch'], r['fear'], r['death'], r['ghost'], r['etype'], r['arch']))

    fails = []
    et = Counter(r['etype'] for r in rows); tot = len(rows)
    print('\n== 体检项 ==')
    # ① 章尾类型：省略+惊叹合计应 ≥20%（原作 37.2%），全零=失能与超带均警示
    hook = (et['ellipsis'] + et['exclaim']) / tot * 100
    ok = hook >= 20
    print('① 章尾钩子(省略+惊叹)=%.1f%%  原作37.2%%  [' % hook, 'PASS' if ok else 'FAIL', ']')
    if not ok: fails.append('章尾钩子')
    # ② 高潮章：≥10%（原作13.3%）
    hi = sum(1 for r in rows if r['arch'] == '高潮章') / tot * 100
    ok = hi >= 10
    print('② 高潮章占比=%.1f%%  原作13.3%%  [' % hi, 'PASS' if ok else 'FAIL', ']')
    if not ok: fails.append('高潮章缺位')
    # ③ 结算章：每个单元≥1（全书≥10%章达到≥1.5倍章长亦认，此处按≥2800字严格）
    settle = [r for r in rows if r['arch'] == '结算章']
    ok = len(settle) >= max(1, tot // 30)
    print('③ 结算章=%d章(要求≥%d)  [' % (len(settle), max(1, tot // 30)), 'PASS' if ok else 'FAIL', ']')
    if not ok: fails.append('结算章缺位')
    # ④ 死亡节拍：全书均值 ≥3.0/章（原作常规4.5，允许同文规模折抵）
    d = statistics.mean(r['death'] for r in rows)
    ok = d >= 3.0
    print('④ 死亡节拍=%.1f/章  原作常规4.5  [' % d, 'PASS' if ok else 'FAIL', ']')
    if not ok: fails.append('死亡节拍过软')
    # ⑤ 恐怖洼地：不得连续≥3章 fear<2
    holes = []
    run = []
    for r in rows:
        if r['fear'] < 2: run.append(r['ch'])
        else:
            if len(run) >= 3: holes.append(run)
            run = []
    if len(run) >= 3: holes.append(run)
    ok = not holes
    print('⑤ 恐怖洼地(连续≥3章fear<2)=%s  [' % (holes if holes else '无'), 'PASS' if ok else 'FAIL', ']')
    if not ok: fails.append('恐怖洼地: ' + ','.join('第%d-%d章' % (h[0], h[-1]) for h in holes))

    if units_arg:
        print('\n== 单元聚合 ==')
        for seg in units_arg.split(','):
            rng, name = seg.split(':')
            a, b = (int(x) for x in rng.split('-'))
            sel = [r for r in rows if a <= r['ch'] <= b]
            if not sel: continue
            hi_n = sum(1 for r in sel if r['arch'] == '高潮章')
            hi_f = sum(1 for r in sel if r['fear'] >= 12)
            el = sum(1 for r in sel if r['etype'] in ('ellipsis', 'exclaim'))
            dd = statistics.mean(r['death'] for r in sel)
            ff = statistics.mean(r['fear'] for r in sel)
            flag = '⚠' if (hi_n == 0 or el == 0) else ' '
            print('%s(%d-%d) %d章 fear均%.1f death均%.1f 高潮%d(近高潮%d) 悬置/惊叹尾%d %s'
                  % (name, a, b, len(sel), ff, dd, hi_n, hi_f, el, flag))

    print('\n结论: ' + ('全部通过' if not fails else '待修项 → ' + '；'.join(fails)))
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
