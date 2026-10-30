#!/usr/bin/env python3
"""逐段回听 → 剪掉段尾空白 → 统一规格 → 拼接。
用法：python3 assemble.py script.json [--out 成片_完整版.mp4] [--lang zh] [--size 宽x高（默认保持源尺寸）]
- script.json：[{"id","t",...}]（和 build_tasks.py 同一份）；生成的片段在 gen/<段 id>.mp4（grok_generate.py 的输出）
- 每段：whisper 转写（中性提示，不用 --prompt 原文，免得漏前半句）→ 和文稿比准确率 → 只保留到说完后 0.25 秒
- comfy 锚点段（gen/<id>.meta.json 写了 anchors）整段保留：最后一帧才是锚点，剪掉接缝就接不上
- 全部是 comfy 段时，拼完再跑 warp_eyes.py 缩眼高（persona.json 的 comfy.eye_warp，1 = 不缩；要装 uv）。有 grok 段就不缩，免得连 grok 的眼睛一起缩
- 比准确率前两边都繁转简（要装 opencc）、中文数字转阿拉伯数字，所以繁体稿、「八秒」和「8 秒」都不会被误判
- 输出 cut/<id>.mp4（30fps、48k 立体声）、cut/<id>.json（逐字时间，align.py 用）、cut/qa.json、拼接好的 --out（-16 LUFS）
- 准确率 < 85% 的段打 ⚠，先人工听；真念错就单独重拍那段"""
import json, subprocess, difflib, re, os, shutil, sys
from pathlib import Path
a = sys.argv[1:]
if len(a) < 1: sys.exit(__doc__)
S = json.load(open(a[0]))
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
out_name, lang, size = opt('--out', '成片_完整版.mp4'), opt('--lang', 'zh'), opt('--size', '')
WM = os.environ.get('WHISPER_MODEL') or next((p for p in map(os.path.expanduser, ['~/Library/Application Support/Murmur/models/ggml-medium-q5_0.bin', '~/models/ggml-medium-q5_0.bin', '~/.cache/whisper/ggml-medium-q5_0.bin', '~/models/ggml-medium.bin']) if os.path.exists(p)), '~/models/ggml-medium-q5_0.bin')
OPENCC = shutil.which('opencc')   # 可选：没装就不做繁转简，繁体稿的准确率会偏低
DIGIT = dict(zip('零〇一二两三四五六七八九', (0, 0, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9)))
UNIT = {'十': 10, '百': 100, '千': 1000}

def cn_int(run):
    """二零二六 → 2026（逐位）；两千零二十六 → 2026（带单位）。万、亿留原字，所以「三千万」和「3000万」都变成 3000万"""
    if not set(run) & set(UNIT): return ''.join(str(DIGIT[c]) for c in run)
    n = cur = 0
    for c in run:
        if c in UNIT: n += (cur or 1) * UNIT[c]; cur = 0
        else: cur = DIGIT[c]
    return str(n + cur)

def clean(s):
    """文稿和 whisper 结果都过一遍：繁转简、中文数字转阿拉伯数字（whisper 习惯写 8秒、1.5版），再去标点。
    「一下」「统一」也会变成「1下」「统1」，两边一样所以不影响比对"""
    if OPENCC: s = subprocess.run([OPENCC, '-c', 't2s'], input=s, capture_output=True, text=True, check=True).stdout   # 失败时两边都成空字串会全判 100%，所以不吞错
    s = re.sub('[零〇一二两三四五六七八九十百千]+', lambda m: cn_int(m[0]), s)
    s = re.sub(r'(\d)点(\d)', r'\1.\2', s)
    return re.sub(r'[\s，。、：；！？,.:;!?“”「」]', '', s).lower()

Path('cut').mkdir(exist_ok=True); rep, metas = [], []
for s in S:
    sid = s['id']; src = f"gen/{sid}.mp4"; wav = f'cut/{sid}.wav'
    meta = json.load(open(f'gen/{sid}.meta.json')) if os.path.exists(f'gen/{sid}.meta.json') else {}   # comfy_generate.py 写的
    metas.append(meta)
    lg = s.get('lang_code', lang)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-ar', '16000', '-ac', '1', wav], check=True)
    cmd = ['whisper-cli', '-m', WM, '-l', lg] + (['--prompt', '以下是普通话的句子。', '-ml', '1'] if lg == 'zh' else []) + ['-oj', '-of', f'cut/{sid}', '-f', wav]
    subprocess.run(cmd, capture_output=True)
    d = [t for t in json.load(open(f'cut/{sid}.json', errors='replace'))['transcription'] if t['text'].strip() and not t['text'].strip().startswith('[')]
    heard = ''.join(t['text'] for t in d)
    st = min(t['offsets']['from'] for t in d) / 1000 if d else 0; en = max(t['offsets']['to'] for t in d) / 1000 if d else 0
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.split(','))
    sz = size or f'{w - w % 2}x{h - h % 2}'          # 保持源尺寸（Grok 9:16 720p 是 720×1280，别拉成 720×1440）
    acc = difflib.SequenceMatcher(None, clean(s['t']), clean(heard)).ratio()
    keep = dur if meta.get('anchors') else min(dur, en + 0.25)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-t', f'{keep:.3f}', '-vf', f'scale={sz.replace("x", ":")}:flags=lanczos,fps=30,format=yuv420p',
                    '-af', f'aresample=48000,afade=t=out:st={max(0, keep - 0.12):.3f}:d=0.12', '-ac', '2', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', f'cut/{sid}.mp4'], check=True)
    rep.append(dict(id=sid, acc=round(acc, 3), speech=[round(st, 2), round(en, 2)], keep=round(keep, 2), src_dur=round(dur, 2), heard=heard))
    print(f"{'⚠' if acc < 0.85 else ' '}{sid:5s} 准确率 {acc:.0%}  说话 {st:.2f}–{en:.2f}s  保留 {keep:.2f}/{dur:.2f}s{'（锚点段整段保留）' if meta.get('anchors') else ''}  听到：{heard}")
json.dump(rep, open('cut/qa.json', 'w'), ensure_ascii=False, indent=1)
open('cut/list.txt', 'w').write(''.join(f"file '{s['id']}.mp4'\n" for s in S))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'cut/list.txt', '-c', 'copy', 'cut/joined.mp4'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', 'cut/joined.mp4', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out_name], check=True)
print('拼接完成', out_name, round(sum(r['keep'] for r in rep), 2), '秒')

warp = json.load(open(Path(__file__).resolve().parent.parent / 'persona.json')).get('comfy', {}).get('eye_warp', 1)
comfy = [m.get('backend') == 'comfy' for m in metas]
if warp < 1 and all(comfy):
    if shutil.which('uv'):
        tmp = str(Path(out_name).with_suffix('.warp.mp4'))
        subprocess.run(['uv', 'run', '--no-project', '--with', 'mediapipe', '--with', 'opencv-python-headless', 'python', '-I',
                        str(Path(__file__).with_name('warp_eyes.py')), out_name, tmp, str(warp)], check=True)
        os.replace(tmp, out_name)
        print(f'缩眼高 {warp}（H3 会把眼睛画大，persona.json 的 comfy.eye_warp）')
    else:
        print('没装 uv，跳过缩眼高：装好 uv 后跑 scripts/warp_eyes.py', out_name)
elif warp < 1 and any(comfy):
    print('有 grok 段也有 H3 段，没缩眼高（会连 grok 段一起缩）')
