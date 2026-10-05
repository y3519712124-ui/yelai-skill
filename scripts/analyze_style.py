# -*- coding: utf-8 -*-
"""网文文风定量统计：句长/对话比/拟声词/高频词/章首章尾模式等"""
import re
import sys
import json
import collections

def load_chapters(path, limit=None):
    text = open(path, encoding='utf-8').read()
    parts = re.split(r'^@@@CHAP (\d+)\t([^\t]+)\t(\d+)字\n', text, flags=re.M)
    chaps = []
    for i in range(1, len(parts), 4):
        chaps.append({'idx': int(parts[i]), 'title': parts[i+1].strip(), 'body': parts[i+3].strip()})
        if limit and len(chaps) >= limit:
            break
    return chaps

def sentences(text):
    body = re.sub(r'\n', '', text)
    parts = re.split(r'([。！？!?]+)', body)
    sents, cur = [], ''
    for p in parts:
        cur += p
        if re.match(r'^[。！？!?]+$', p):
            if cur.strip():
                sents.append(cur)
            cur = ''
    if cur.strip():
        sents.append(cur)
    return [s for s in sents if len(s.strip()) > len(s.strip()) - len(s.strip().lstrip('。！？!?')) or s.strip()]

def main():
    path = sys.argv[1]
    n_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    chaps = load_chapters(path, n_limit)
    full = '\n'.join(c['body'] for c in chaps)
    res = {'file': path, 'chapters_analyzed': len(chaps), 'chars': len(full)}

    # 句长
    sents = sentences(full)
    slens = [len(s) for s in sents]
    res['total_sentences'] = len(sents)
    res['avg_sent_len'] = round(sum(slens) / max(1, len(slens)), 1)
    res['short_sent_ratio(<=8字)'] = round(sum(1 for l in slens if l <= 8) / len(slens), 3)
    res['long_sent_ratio(>=25字)'] = round(sum(1 for l in slens if l >= 25) / len(slens), 3)

    # 段落
    paras = [p for p in full.split('\n') if p.strip()]
    res['total_paras'] = len(paras)
    res['avg_para_len'] = round(len(full) / max(1, len(paras)), 1)
    res['one_line_para_ratio'] = round(sum(1 for p in paras if len(p) <= 15) / len(paras), 3)

    # 对话行占比
    dialog = [p for p in paras if p.strip().startswith('"') or p.strip().startswith('"')]
    res['dialog_line_ratio'] = round(len(dialog) / max(1, len(paras)), 3)

    # 标点密度（每千字）
    for name, pat in [('ellipsis(……)', '……'), ('dash(——)', '——'), ('exclaim(！)', '[！!]'), ('question(？)', '[？?]')]:
        res[f'{name}/千字'] = round(full.count(pat) / len(full) * 1000, 2)

    # 拟声词
    onom = re.findall(r'[咯咔咯吱嗖咚轰嗡嗒啪哗滴答叮当哼嗡呜呼嚎嘶嗥哗啦轰隆窸窣簌扑通咯噔嘎吱怦怦咚咚当当滴滴哒哒滴答沙沙哗哗呼呼簌簌飒飒]{2,4}', full)
    onom_counts = collections.Counter(re.findall(r'(咯咯|咔哒|窸窸窣窣|窸窣|沙沙|哗啦|轰隆|扑通|咯噔|嘎吱|滴答|咚咚|怦怦|嗒|嗖|呜|嗡|嘶|簌簌|飒飒|咯吱|咔嚓|噗|噔|咚)', full))
    res['onomatopoeia_top20'] = onom_counts.most_common(20)

    # 高频词（2-4字，去停用词）
    STOP = set('他们她们我们你们自己一个没有已经知道什么这个那个就是但是因为所以如果现在的时候东西样子地方开始出来上去下来起来事情问题觉得感觉看着来到知道这些那些一声顿时瞬间整个直接突然终于还是只是不过然后可是随之接着随后立即立刻马上顿时'.split())
    words = re.findall(r'[一-龥]{2,4}', full)
    wc = collections.Counter(w for w in words if w not in STOP and not re.match(r'^第[一二三四五六七八九十百千\d]+', w))
    res['top_words_50'] = wc.most_common(50)

    # 章首模式（前60章）
    starts = collections.Counter()
    for c in chaps:
        body = c['body']
        lines = [l for l in body.split('\n')[1:] if l.strip()]
        if not lines:
            continue
        first = lines[0].strip()
        if first.startswith('"'):
            starts['对话开头'] += 1
        elif re.match(r'^第.+章$', first):
            second = lines[1].strip() if len(lines) > 1 else ''
            starts['场景/时间开头' if not second.startswith('"') else '对话开头'] += 1
        elif re.search(r'\d+月|\d+日|凌晨|清晨|中午|夜晚|深夜|夜里|早上|晚上|次日|第二天', first):
            starts['时间锚点开头'] += 1
        else:
            starts['叙述/动作开头'] += 1
    res['chapter_start_patterns'] = dict(starts)

    # 章尾模式（前60章）
    ends = collections.Counter()
    for c in chaps:
        body = c['body'].rstrip()
        last = body.split('\n')[-1].strip()
        if last.startswith('"') or '"' in last[-15:]:
            ends['对话收尾'] += 1
        elif re.search(r'[？?]$', last):
            ends['问句收尾'] += 1
        elif re.search(r'(！|……)$', last):
            ends['惊叹/悬置收尾'] += 1
        elif re.search(r'[。]$', last):
            ends['陈述收尾'] += 1
        else:
            ends['其他'] += 1
    res['chapter_end_patterns'] = dict(ends)

    # 恐怖感官词频
    sense = {}
    for k, pat in [('视觉-黑/暗', r'漆黑|黑暗|昏暗|阴沉'), ('听觉-静', r'安静|寂静|死寂|鸦雀无声|静得'),
                   ('温度-冷', r'冰冷|阴冷|发冷|寒意|凉意'), ('嗅觉', r'腥味|腐朽|恶臭|气味|血腥味'),
                   ('触觉-黏腻', r'黏|滑腻|潮湿'), ('声音-耳语', r'耳畔|耳边|低语|呢喃|传来')]:
        sense[k] = len(re.findall(pat, full))
    res['horror_sense_words'] = sense

    out = sys.argv[3] if len(sys.argv) > 3 else None
    txt = json.dumps(res, ensure_ascii=False, indent=1)
    if out:
        open(out, 'w', encoding='utf-8').write(txt)
    print(txt)

if __name__ == '__main__':
    main()
