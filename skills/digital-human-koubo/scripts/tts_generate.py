#!/usr/bin/env python3
"""script.json → 每段用 CosyVoice 3 配音（ssh 到 GPU 机器跑零样本克隆）→ audio/<段 id>.wav，再把 "audio" 写回 script.json。

用法：python3 tts_generate.py script.json [--only s1,s3] [--force] [--host aiko]
- comfy 后端的前一步：配好音再跑 build_tasks.py --backend comfy、comfy_generate.py
- 参考音档：persona.json → voice.tts_ref（用户本人主播是 other_hosts.me.tts_ref），路径相对技能目录；只克隆本人或明确授权的声音
- 机器和路径在 persona.json 的 tts 那一节；--host > 环境变量 TTS_SSH_HOST > tts.ssh_host。要能免密码 ssh 过去
- 已有 "audio" 的段跳过；--force 全部重配，--only 只重配指定的段
- "tts_text"：只在个别词念错时用，改的是送进 TTS 的文字，字幕和回听仍对照 "t"
- 回听：whisper 转写后只算中文字的字错率（夹英文的句子英文另算召回率，因为 whisper 会把英文翻成中文）。
  字错率超过 tts.max_cer 就换 seed 重配，最多 tts.retries 次，还不过就留最好的一次并标 ⚠。英文召回率低于 80% 也标 ⚠，但不重配
- 超过 15 秒的段标 ⚠：build_tasks.py 会拒绝，先把台词拆短
- 和 comfy_generate.py 共用同一张显卡，两个不要同时跑
"""
import json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = json.loads((HERE / "persona.json").read_text())
T = P["tts"]
WM = os.environ.get("WHISPER_MODEL") or next((p for p in map(os.path.expanduser, ["~/Library/Application Support/Murmur/models/ggml-medium-q5_0.bin", "~/models/ggml-medium-q5_0.bin", "~/.cache/whisper/ggml-medium-q5_0.bin", "~/models/ggml-medium.bin"]) if os.path.exists(p)), "~/models/ggml-medium-q5_0.bin")
OPENCC = shutil.which("opencc")   # 繁体稿要靠它转简体才比得准，没装时字错率会偏高
DIGIT = dict(zip("零〇一二两三四五六七八九", (0, 0, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9)))
UNIT = {"十": 10, "百": 100, "千": 1000}

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def main():
    src = Path(sys.argv[1]); S = json.loads(src.read_text())
    only = set(arg("--only", "").split(",")) - {""}
    host = arg("--host") or os.environ.get("TTS_SSH_HOST") or T["ssh_host"]
    if only:
        todo = [s for s in S if s["id"] in only]
    else:
        todo = [s for s in S if "--force" in sys.argv or not s.get("audio")]
    if not todo:
        print("每段都有音轨了（要重配加 --force，或 --only 指定段）"); return
    if not OPENCC:
        print("· 没装 opencc：繁体稿的字错率会偏高、多重配几次。装法：brew install opencc")
    refs = {s["id"]: reference(s) for s in todo}
    out = src.parent / "audio"; out.mkdir(exist_ok=True)
    best, pending = {}, todo
    for attempt in range(T["retries"] + 1):
        seed = T["seed"] + attempt
        print(f"配音 {len(pending)} 段（seed {seed}）→ {host}")
        wavs = synthesize(host, pending, refs, seed)
        for s in pending:
            r = dict(check(wavs[s["id"]], s), seed=seed, wav=wavs[s["id"]])
            old = best.get(s["id"])
            if old is None or (r["cer"] or 0) < (old["cer"] or 0):
                best[s["id"]] = r
        pending = [s for s in pending if (best[s["id"]]["cer"] or 0) > T["max_cer"]]
        if not pending:
            break
    for s in todo:
        r = best[s["id"]]
        dst = out / f"{s['id']}.wav"
        shutil.copy(r["wav"], dst)
        s["audio"] = str(dst.relative_to(src.parent))
        report(s, r)
    src.write_text(json.dumps(S, ensure_ascii=False, indent=1))
    print(f"音轨在 {out}/，script.json 的 \"audio\" 已更新；下一步 build_tasks.py --backend comfy")

def reference(s):
    """这一段用哪位主播的参考音档。文件不在就停下，说清楚要放什么。"""
    ref = P["other_hosts"]["me"]["tts_ref"] if s.get("host", "tank") == "me" else P["voice"]["tts_ref"]
    wav = HERE / ref["wav"]
    if not wav.exists():
        sys.exit(f"{s['id']} 缺参考音档 {wav}：放 10–30 秒本人或明确授权的干净朗读，逐字稿写进 persona.json 的 tts_ref.text（见 references/voice.md）")
    return dict(wav=wav, text=ref["text"])

def synthesize(host, segs, refs, seed):
    """打包成一个 job 传到 GPU 机器跑 cosyvoice_batch.py，再把 wav 抓回本机临时目录。回传 {段 id: wav 路径}。"""
    name = time.strftime("%Y%m%d-%H%M%S") + f"-s{seed}"
    job = Path(tempfile.mkdtemp()) / name
    (job / "refs").mkdir(parents=True)
    ref_names = {}
    for r in refs.values():
        if r["wav"] not in ref_names:
            ref_names[r["wav"]] = f"refs/{len(ref_names)}{r['wav'].suffix}"
            shutil.copy(r["wav"], job / ref_names[r["wav"]])
    segments = [dict(id=s["id"], text=s.get("tts_text") or s["t"], ref_wav=ref_names[refs[s["id"]]["wav"]], ref_text=refs[s["id"]]["text"]) for s in segs]
    (job / "job.json").write_text(json.dumps(dict(repo=T["repo"], model_dir=T["model_dir"], seed=seed, segments=segments), ensure_ascii=False, indent=1))
    shutil.copy(Path(__file__).parent / "remote" / "cosyvoice_batch.py", job)
    remote = f"{T['work_dir']}/{name}"
    home_rel = lambda p: p.removeprefix("~/")   # scp 的远端路径相对家目录，不展开 ~
    ssh(host, f"mkdir -p {T['work_dir']}")
    run(["scp", "-q", "-r", str(job), f"{host}:{home_rel(T['work_dir'])}/"])
    r = ssh(host, f"cd {remote} && flock {T['gpu_lock']} {T['python']} cosyvoice_batch.py job.json 2>&1", check=False)
    done = [json.loads(l.split(" ", 1)[1]) for l in r.stdout.splitlines() if l.startswith("KOUBO_TTS ")]
    if r.returncode or len(done) != len(segs):
        sys.exit(f"{host} 上配音失败（exit {r.returncode}），最后几行：\n" + "\n".join((r.stdout + r.stderr).splitlines()[-15:]))
    (job / "out").mkdir()
    run(["scp", "-q", f"{host}:{home_rel(remote)}/out/*.wav", str(job / "out")])
    return {s["id"]: job / "out" / f"{s['id']}.wav" for s in segs}

def ssh(host, cmd, check=True):
    return run(["ssh", "-o", "BatchMode=yes", host, cmd], check=check)

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"{' '.join(cmd[:3])} … 失败：{r.stderr.strip() or r.stdout.strip()}")
    return r

def check(wav, s):
    """whisper 回听。普通话段：台词被英文隔开的每段中文，各自在转写里找最像的一段算编辑距离（近似子字串比对）；
    有英文时另跑 -l en 算英文单字召回率。其他语言不回听（cer 为 None）。"""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)], capture_output=True, text=True).stdout or 0)
    lang = s.get("lang", "Mandarin Chinese")
    if not (lang.startswith("Mandarin") or lang == "Chinese"):
        return dict(cer=None, en=None, heard="", dur=dur)
    heard = transcribe(wav, "zh")
    ref, hyp = tokens(s["t"]), tokens(heard)
    han = lambda t: bool(re.match(r"[一-鿿\d]", t))
    spans = [m.split() for m in " ".join(t if han(t) else "|" for t in ref).split("|") if m.strip()]
    hz = [t for t in hyp if han(t)]
    cer = sum(near(sp, hz) for sp in spans) / max(1, sum(map(len, spans)))
    en = None
    if en_ref := [t for t in ref if not han(t)]:
        left = tokens(transcribe(wav, "en"))
        hit = 0
        for t in en_ref:
            if t in left: left.remove(t); hit += 1
        en = hit / len(en_ref)
    return dict(cer=cer, en=en, heard=heard, dur=dur)

def transcribe(wav, lang):
    with tempfile.TemporaryDirectory() as d:
        w = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "1", "-ar", "16000", str(w)], check=True)
        prompt = ["--prompt", "以下是普通话的句子。"] if lang == "zh" else []
        out = subprocess.run(["whisper-cli", "-m", WM, "-l", lang, *prompt, "-nt", "-f", str(w)], capture_output=True, text=True).stdout
    return " ".join(out.split())

def tokens(s):
    """繁转简、中文数字转阿拉伯数字、转小写，再切成汉字、英文单词和数字。"""
    if OPENCC: s = subprocess.run([OPENCC, "-c", "t2s"], input=s, capture_output=True, text=True, check=True).stdout
    s = re.sub("[零〇一二两三四五六七八九十百千]+", lambda m: cn_int(m[0]), s.lower())
    return re.findall(r"[a-z]+(?:['’][a-z]+)*|\d+|[一-鿿]", s)

def cn_int(run):
    if not set(run) & set(UNIT): return "".join(str(DIGIT[c]) for c in run)
    n = cur = 0
    for c in run:
        if c in UNIT: n += (cur or 1) * UNIT[c]; cur = 0
        else: cur = DIGIT[c]
    return str(n + cur)

def near(r, h):
    """r 在 h 里最像的一段子字串的编辑距离（开头和结尾不计成本）。"""
    prev = [0] * (len(h) + 1)
    for i, x in enumerate(r, 1):
        cur = [i]
        for j, y in enumerate(h, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return min(prev)

def report(s, r):
    long = r["dur"] > P["model"]["max_seconds"]
    bad = long or (r["cer"] or 0) > T["max_cer"] or (r["en"] is not None and r["en"] < 0.8)
    cer = "未回听" if r["cer"] is None else f"字错率 {r['cer']:.0%}"
    en = "" if r["en"] is None else f"  英文 {r['en']:.0%}"
    note = "  超过 15 秒，先把台词拆短" if long else ""
    print(f"{'⚠' if bad else ' '}{s['id']:5s} {r['dur']:5.1f}s  {cer}{en}  seed {r['seed']}{note}  听到：{r['heard']}")

if __name__ == "__main__":
    main()
