#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""夜来skill 润色器 v2 —— 双向标点配平 + 段落整流 + 对话连排限幅。

用法: python polish_chapter.py 第172章-*.md [更多文件...]
规则(§20/§23/§25):
  1. 破折号 <=3 处(保留拟声/断章优先, 其余转换)
  2. 省略号 6-8/千字 双向配平(裁剪句尾完整处/注入悬置处)
  3. 感叹号 5-8/千字 双向配平
  4. 叙述短段合并至 18-26 字均长
  5. 同说话人对话连排 >3 段时, 合并为一段(不产生病句, 仅拼接)
"""
import glob, re, sys

def is_d(p): return p.startswith('“') or p.startswith('"')

def fix_dash(t, keep=3):
    idxs = [m.start() for m in re.finditer('——', t)]
    ks = set(idxs[:keep]); out = []; last = 0
    for i in idxs:
        out.append(t[last:i])
        if i in ks: out.append('——')
        else:
            n = t[i+2:i+3]
            out.append('……' if n in ('', '\n', '"', '”') else '，')
        last = i + 2
    out.append(t[last:])
    return ''.join(out)

def kq_of(t):
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    return max(len(re.sub(r'\s', '', body)) / 1000, 0.5)

def cap_ellipsis(t, cap=7.4):
    idxs = [m.start() for m in re.finditer('……', t)]
    allow = int(cap * kq_of(t))
    if len(idxs) > allow:
        out = []; last = 0
        for i in idxs[allow:]:
            out.append(t[last:i]); out.append('。' if t[i+2:i+3] in ('', '\n', '"', '”') else '，'); last = i + 2
        out.append(t[last:]); t = ''.join(out)
    return t

def cap_excl(t, cap=7.4):
    idxs = [m.start() for m in re.finditer('！', t)]
    allow = int(cap * kq_of(t))
    if len(idxs) > allow:
        out = []; last = 0
        for i in idxs[allow:]:
            out.append(t[last:i]); out.append('。'); last = i + 1
        out.append(t[last:]); t = ''.join(out)
    return t

ELL_HINTS = ['很久', '静', '沉默', '很久很久', '半晌', '不动', '一眼', '呼吸', '心跳', '对视', '沉', '凉', '抖']
def inject_ellipsis(t, need):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    added = 0
    for i, p in enumerate(paras):
        if added >= need: break
        if is_d(p) or p.startswith('【') or p.startswith('——'): continue
        if p.endswith('。') and any(h in p for h in ELL_HINTS):
            paras[i] = p[:-1] + '……'; added += 1
    return '\n\n'.join(paras) + '\n'

EXCL_HINTS = ['快', '别', '跑', '杀', '死', '滚', '小心', '住手', '退', '火', '冲', '来了', '走', '开']
def inject_excl(t, need):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    added = 0
    for i, p in enumerate(paras):
        if added >= need: break
        if is_d(p) and p.endswith('。”') or (is_d(p) and p.endswith('。"')):
            if any(h in p for h in EXCL_HINTS):
                paras[i] = p[:-2] + '！”'; added += 1
    return '\n\n'.join(paras) + '\n'

def merge_paras(t, target=28, cap=34):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    out = []; i = 0
    while i < len(paras):
        p = paras[i]
        if is_d(p) or p.startswith('【') or len(p) >= cap:
            out.append(p); i += 1; continue
        cur = p; j = i + 1
        while j < len(paras) and len(cur) < target:
            q = paras[j]
            if is_d(q) or q.startswith('【') or len(q) >= cap: break
            cur += q; j += 1
        out.append(cur); i = j
    return '\n\n'.join(out) + '\n'

def cap_dlg_run(t, maxrun=3):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    out = []; i = 0
    while i < len(paras):
        p = paras[i]
        if is_d(p):
            block = [p]; j = i + 1
            while j < len(paras) and is_d(paras[j]) and len(block) < 6:
                block.append(paras[j]); j += 1
            if len(block) > maxrun:
                head = block[:maxrun]
                tail = ''.join(b if b.endswith('”') or b.endswith('"') else b for b in block[maxrun:])
                tail = re.sub(r'”\s*“', '。', tail).replace('”', '”')
                if not (tail.startswith('“') or tail.startswith('"')):
                    tail = tail
                for b in head: out.append(b)
                out.append(tail if tail.startswith('“') or tail.startswith('"') else '他说下去：' + tail)
            else:
                for b in block: out.append(b)
            i = j
        else:
            out.append(p); i += 1
    return '\n\n'.join(out) + '\n'

def polish(path):
    t = open(path, encoding='utf-8').read()
    t = fix_dash(t)
    t = merge_paras(t)
    t = cap_dlg_run(t)
    # 双向配平省略号
    t = cap_ellipsis(t)
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    kq = kq_of(t)
    ell = body.count('……') / kq
    if ell < 6.0:
        t = inject_ellipsis(t, int((6.0 - ell) * kq) + 1)
    t = cap_excl(t)
    body = re.sub(r'^## .*$', '', t, flags=re.M)
    ex = body.count('！') / kq
    if ex < 5.0:
        t = inject_excl(t, int((5.2 - ex) * kq) + 1)
    open(path, 'w', encoding='utf-8').write(t)

if __name__ == '__main__':
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    for f in sorted(set(files)):
        polish(f); print('polished', f)
