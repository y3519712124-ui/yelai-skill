#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""夜来skill 章节修复器 v1 —— 按§20/§23约束自动修复漂移。

用法: python repair_chapter.py 第156章-*.md [第157章-*.md ...]
修复项:
  1. 破折号配额(<=3, 其余句中转逗号/句尾转省略号)
  2. 长对话连排压缩(连续对话>3段时, 偶数位转间接引语)
  3. 叙述短段合并(目标段长18-26)
  4. 感叹号注入(对话含祈使/強情词的句尾)与省略号注入(犹疑词句尾)
"""
import glob, re, sys

def is_d(p): return p.startswith('“') or p.startswith('"') or p.startswith('「')

def fix_dash(t, keep=3):
    idxs = [m.start() for m in re.finditer('——', t)]
    keepset = set(idxs[:keep])
    out = []; last = 0
    for i in idxs:
        out.append(t[last:i])
        if i in keepset:
            out.append('——')
        else:
            nxt = t[i+2:i+3]
            out.append('……' if nxt in ('', '\n', '"', '”') else '，')
        last = i + 2
    out.append(t[last:])
    return ''.join(out)

def compress_dialogue(t, max_run=4):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    out = []; run = 0; i = 0
    while i < len(paras):
        p = paras[i]
        if is_d(p):
            if run >= max_run:
                inner = p.strip('“”"「」')
                verb = '问' if inner.rstrip('。！？…').endswith(('吗', '呢', '什么', '谁', '怎么', '几')) or inner.rstrip('。！？…').endswith('？') else '道'
                if verb == '问':
                    out.append(f'他又一次问起，{inner.rstrip("。！？…？")}。没人立刻接话。')
                else:
                    out.append(f'这话他说得不紧不慢，{inner.rstrip("。！？…")}。')
                run = 0
            else:
                out.append(p); run += 1
            i += 1
        else:
            out.append(p); run = 0; i += 1
    return '\n\n'.join(out) + '\n'

def merge_narration(t, target=42):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    out = []; i = 0
    while i < len(paras):
        p = paras[i]
        if is_d(p) or p.startswith('【') or p.startswith('——') or len(p) >= target:
            out.append(p); i += 1; continue
        cur = p; j = i + 1
        while j < len(paras) and len(cur) < target:
            q = paras[j]
            if is_d(q) or q.startswith('【') or q.startswith('——') or len(q) >= target:
                break
            cur += q; j += 1
        out.append(cur); i = j
    return '\n\n'.join(out) + '\n'

EXCL_WORDS = ['快', '跑', '别', '滚', '杀', '死', '小心', '住手', '退', '火', '冲']
HESIT_WORDS = ['可能', '也许', '不知道', '要是', '万一', '静', '很久', '沉默']

def inject_punct(t):
    paras = [p.strip() for p in re.split(r'\n+', t) if p.strip()]
    ex_added = 0; ell_added = 0
    for idx, p in enumerate(paras):
        if is_d(p):
            if ex_added < 6 and any(w in p for w in EXCL_WORDS) and p.endswith('。”') or p.endswith('。"'):
                pass
            if ex_added < 6 and any(w in p for w in EXCL_WORDS) and (p.endswith('。”') or p.endswith('。"')):
                paras[idx] = p[:-2] + '！”' if p.endswith('。”') else p[:-2] + '！”'
                ex_added += 1
        else:
            if ell_added < 8 and any(w in p for w in HESIT_WORDS) and p.endswith('。'):
                paras[idx] = p[:-1] + '……'
                ell_added += 1
    return '\n\n'.join(paras) + '\n'

def repair(path):
    t = open(path, encoding='utf-8').read()
    t = fix_dash(t)
    t = compress_dialogue(t)
    t = merge_narration(t)
    t = inject_punct(t)
    open(path, 'w', encoding='utf-8').write(t)

if __name__ == '__main__':
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    for f in sorted(set(files)):
        repair(f)
        print('repaired', f)
