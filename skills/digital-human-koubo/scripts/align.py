#!/usr/bin/env python3
"""逐字时间轴：把 assemble.py 的 cut/<id>.json（whisper 逐字）和文稿对齐，输出剪辑模板用的 tl.json。
用法：python3 align.py script.json [--out edit/src/tl.json]
tl.json = {"total": 秒, "segs": [{"i","id","start","end","text","chars":{"字符下标": 秒}}]}（chars 是整片绝对时间）"""
import json, difflib, shutil, subprocess, sys
from pathlib import Path

def t2s_table(text):
    """文稿里繁体字 → 简体字的逐字对照（whisper 只输出简体），比对时换字、下标不变。没装 opencc 就是空表"""
    cs = sorted({c for c in text if not c.isspace()}); oc = shutil.which('opencc')
    if not oc: return {}
    out = subprocess.run([oc, '-c', 't2s'], input='\n'.join(cs), capture_output=True, text=True, check=True).stdout.split('\n')
    return {a: b for a, b in zip(cs, out) if len(b) == 1 and a != b}

a = sys.argv[1:]
if not a: sys.exit(__doc__)
S = json.load(open(a[0])); Q = {r['id']: r for r in json.load(open('cut/qa.json'))}
T2S = t2s_table(''.join(s['t'] for s in S))
out = a[a.index('--out') + 1] if '--out' in a else 'edit/src/tl.json'
PUNCT = set('，。、：；！？,.:;!? “”「」')
T0 = 0.0; segs = []
for i, s in enumerate(S, 1):
    sid, text = s['id'], s['t']; keep = Q[sid]['keep']
    tk = []
    for t in json.load(open(f'cut/{sid}.json', errors='replace'))['transcription']:
        a0, a1 = t['offsets']['from'] / 1000, t['offsets']['to'] / 1000; tx = t['text'].strip()
        if not tx or tx.startswith('['): continue
        for k, ch in enumerate(tx):
            if ch not in PUNCT: tk.append((T2S.get(ch, ch).lower(), a0 + (a1 - a0) * k / len(tx)))   # 两边用同一张表，日文汉字也对得上
    clean = [(j, T2S.get(ch, ch).lower()) for j, ch in enumerate(text) if ch not in PUNCT]
    A = ''.join(c for _, c in clean); B = ''.join(c for c, _ in tk)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False); st = [None] * len(clean)
    for bl in sm.get_matching_blocks():
        for k in range(bl.size): st[bl.a + k] = tk[bl.b + k][1]
    known = [k for k, v in enumerate(st) if v is not None]
    for k in range(len(st)):
        if st[k] is None:
            lo = max([j for j in known if j < k], default=None); hi = min([j for j in known if j > k], default=None)
            st[k] = 0.0 if lo is None and hi is None else (st[hi] if lo is None else (st[lo] + 0.18 * (k - lo) if hi is None else st[lo] + (st[hi] - st[lo]) * (k - lo) / (hi - lo)))
    cov = sum(bl.size for bl in sm.get_matching_blocks()) / max(1, len(A))
    segs.append(dict(i=i, id=sid, start=round(T0, 3), end=round(T0 + keep, 3), text=text, chars={str(j): round(T0 + st[k], 3) for k, (j, _) in enumerate(clean)}))
    print(f'{i:2d} {sid:5s} 对齐 {cov:.0%}  {T0:.2f}–{T0 + keep:.2f}')
    T0 += keep
Path(out).parent.mkdir(parents=True, exist_ok=True)
json.dump(dict(total=round(T0, 3), segs=segs), open(out, 'w'), ensure_ascii=False, indent=0)
print('total', round(T0, 2), '→', out)
