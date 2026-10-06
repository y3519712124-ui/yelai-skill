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
    声纹带     引语均长15-25字(<10=碎渣化)；分层度>=1.5；主角垄断>=40%(第11项,§34.4)
输出: 每项 PASS/FAIL + 综合判定。退出码 0=全过, 1=有 FAIL。
"""
import glob, re, sys, statistics

FEAR = ['血', '死', '鬼', '尸', '怕', '惊', '惨', '恐']


# ---------- §34.4 声纹带 ----------
# 说话者识别：只认「真说话归属」两种形态——
#   A 前置：X说："…" / X道，"…"（动词后紧跟 ：""，， 等引语标点）
#   B 尾随："…"X说。/"…"X问道。（引语在前、名+动词收尾）
# 叙事句（周迟没说话/不知道/没有人回答/都是道具）一律不归属。
_NAME = r'[\u4e00-\u9fa5]{2,3}'
_VERB = r'(?:说道|低声道|沉声道|冷冷道|幽幽道|开口道|问道|喊道|吼道|骂道|嘀咕|喃喃|回答|开口|[说问喊答吼骂道])'
# A 前置归属：名字(+≤6字插入语)+说话动词+紧跟引号——"周迟没说话"因动词后无引号被天然排除
_LEAD_RE = re.compile(r'(?<![\u4e00-\u9fa5])(' + _NAME + r')[^，。！？…“”\x27\x22]{0,6}' + _VERB + r'[^，。！？…“”\x27\x22]{0,2}[:：，,]?\s*[“\x22]')
# B 尾随归属：名字+动词收尾（"……"周迟说。）
_TAIL_RE = re.compile(r'(?<![\u4e00-\u9fa5])(' + _NAME + ')' + _VERB + r'\s*[。！？…，,]?\s*$')
_GENERIC = set('有人没人无人没有人对方大家众人两人三人四人自己别人所有声音老头老人女人男人小孩姑娘大姐大哥阿姨师傅老板他们她们它们我们你们一个不知那个这个')
_PARTICLE = set('在不又就才还也都便没把被和与去来')

def _clean_name(n):
    """3字名末字若是虚词（老曹在→老曹），回退2字。"""
    if len(n) == 3 and n[-1] in _PARTICLE:
        return n[:-1]
    return n

def _speaker_of(line):
    """取本行的说话者名；无真归属则 None。"""
    m = _LEAD_RE.search(line)
    if m and m.group(1) not in _GENERIC:
        return _clean_name(m.group(1))
    m = _TAIL_RE.search(line)
    if m and m.group(1) not in _GENERIC:
        return _clean_name(m.group(1))
    return None

def _voice_stats(path):
    t = open(path, encoding='utf-8').read()
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    qpat = re.compile(r'“([^”]{1,150})”|"([^"\n]{1,150})"')
    segs = []           # (quote, name_or_None)
    last = None
    for l in lines:
        spk = _speaker_of(l)
        if l.startswith('“') or l.startswith('"'):
            m = qpat.search(l)
            if m:
                q = m.group(1) if m.group(1) is not None else m.group(2)
                segs.append((q, spk if spk else last))
        if spk:
            last = spk
    return segs

def voice_check(path):
    """返回 (items_append_list, detail_str)。多名说话者且样本足够才判带。"""
    segs = _voice_stats(path)
    by = {}
    for q, n in segs:
        if n: by.setdefault(n, []).append(q)
    main = {n: v for n, v in by.items() if len(v) >= 5}
    if len(main) < 2:
        return [], '样本不足(%d名说话者>=5段)' % len(main)
    means = {n: sum(len(x) for x in v) / len(v) for n, v in main.items()}
    top = sorted(means, key=lambda n: -len(by[n]))[:5]
    spread = max(means[n] for n in top) - min(means[n] for n in top)
    lead = top[0]
    lead_len = means[lead]
    lead_share = len(by[lead]) / max(1, len(segs)) * 100
    det = '均长' + '/'.join('%s%.0f' % (n, means[n]) for n in top) + ' 分层%.1f 主角 monopol%.0f%%' % (spread, lead_share)
    items = []
    items.append(('声纹·引语均长', round(lead_len, 1), 10.0 <= lead_len <= 30.0,
                  '带15-25(<10=碎渣化)' if lead_len < 10 else '带15-25'))
    items.append(('声纹·分层度', round(spread, 1), spread >= 1.5, '带>=1.5'))
    return items, det

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

    vi, vdet = voice_check(path)
    for k, v, ok, d in vi:
        add(k, v, ok, d + ' | ' + vdet)

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
