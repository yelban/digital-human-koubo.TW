#!/usr/bin/env python3
"""从一次普通模式的 H3 生成结果里挑锚点帧，建这位主播的锚点库（comfy_generate.py 的锚点模式用）。
用法：uv run --no-project --with mediapipe --with opencv-python-headless python scripts/make_anchors.py tasks.json [--gen gen_bootstrap] [--count 5] [--force]
- tasks.json 就是生成用的那份；按每段的参考图分组，每位主播建一个库：assets/anchors/<参考图文件名>/home.png、a1.png…，加一张 sheet.jpg 给用户看
- 候选：每段音轨静音处的帧（开头 0.3 秒不算），嘴闭着、眼睛睁着；亮度离候选中位数 4 以内；眼高比不超过中位数的 1.1 倍（锚点眼睛大，接缝处就是瞪眼）
- 存档前每张锚点的平均亮度都调成候选中位数：锚点暗 3 左右，用它的那两段整段就跟着暗（长段 H3 会越画越暗，段尾的帧常常暗 3 左右）
- home = 姿势最接近候选中位数的那帧，片头、片尾、换主播处用；a1、a2… 按「歪头角度、头的位置、转头」挑彼此差最多的，
  离 home 不超过 15° 和 0.25 倍两眼距离。每个接缝轮流用一张，停顿时的姿势就不会每次一样
- 锚点都是 H3 自己从参考图画出来的帧：当第一帧不会有开头几帧的脸部跳动，而且同一代、亮度一致，不会像「上一段最后一帧接下一段」那样一段段变暗
- 库已经存在就停下（换锚点会让之后单段重拍接不上），要重建加 --force
- 锚点库是用户自己的生成结果，只放本机（.gitignore 了 assets/anchors/）"""
import json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # uv run python -I 不会把脚本目录放进 sys.path
import cv2, numpy as np
import face

HERE = Path(__file__).resolve().parent.parent
ANCHORS = HERE / "assets" / "anchors"

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def main():
    tasks = json.loads(Path(sys.argv[1]).read_text())
    gen, count, force = Path(arg("--gen", "gen_bootstrap")), int(arg("--count", "5")), "--force" in sys.argv
    by_ref = {}
    for t in tasks: by_ref.setdefault(t["images"][0], []).append(t["id"])
    for ref, ids in by_ref.items():
        out = ANCHORS / Path(ref).stem
        if (out / "home.png").exists() and not force:
            print(f"  {Path(ref).name}：已有锚点库 {out}，跳过（要重建加 --force）"); continue
        cands = [c for sid in ids if (gen / f"{sid}.mp4").exists() for c in candidates(gen / f"{sid}.mp4", sid)]
        picked = choose(cands, count)
        if not picked: sys.exit(f"{Path(ref).name}：{gen}/ 里找不到嘴闭着的静音帧，先用普通模式生成几段（comfy_generate.py --no-anchors --out {gen}）")
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*.png"): old.unlink()
        names = ["home"] + [f"a{i}" for i in range(1, len(picked))]
        luma = np.median([c["luma"] for c in cands])
        for name, c in zip(names, picked):
            c["img"] = np.clip(c["img"].astype(np.float32) * (luma / c["luma"]), 0, 255).round().astype(np.uint8)
            cv2.imwrite(str(out / f"{name}.png"), c["img"])
            print(f"  {name:5s} {c['sid']} 第 {c['n']:3d} 帧  歪头 {c['roll']:+5.1f}°  位置 ({c['center'][0]:.0f},{c['center'][1]:.0f})  "
                  f"转头 {c['turn']:+.3f}  眼高比 {c['eye']:.3f}  亮度 {c['luma']:.1f} → {c['img'].mean():.1f}")
        sheet(picked, names, out / "sheet.jpg")
        print(f"{Path(ref).name}：{len(picked)} 张锚点（{len(cands)} 个候选）→ {out}，先把 sheet.jpg 给用户看")

def candidates(video, sid):
    """静音处、嘴闭着、眼睛睁着的帧"""
    err = subprocess.run(["ffmpeg", "-i", str(video), "-af", "silencedetect=n=-40dB:d=0.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    quiet = list(zip(starts, ends + [1e9] * (len(starts) - len(ends))))
    cap, out, n = cv2.VideoCapture(str(video)), [], 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    while True:
        ok, f = cap.read()
        if not ok: break
        t = n / fps
        if t > 0.3 and any(a + 0.1 <= t <= b - 0.05 for a, b in quiet) and (pts := face.landmarks(f)) is not None:
            p = face.pose(pts)
            if p["mouth"] < 0.03 and p["eye"] > 0.10:
                out.append(dict(p, sid=sid, n=n, img=f, luma=float(f.mean())))
        n += 1
    return out

def choose(cands, count):
    """home = 最接近中位姿势的帧；其余按姿势差最远点逐张挑，跟已挑的每一张都要差够多"""
    if not cands: return []
    luma = np.median([c["luma"] for c in cands]); eye = np.median([c["eye"] for c in cands])
    cands = [c for c in cands if abs(c["luma"] - luma) <= 4 and c["eye"] <= 1.1 * eye] or cands
    iod = np.median([c["iod"] for c in cands])
    vec = lambda c: np.array([c["roll"] / 4, c["center"][0] / (0.12 * iod), c["center"][1] / (0.12 * iod), c["turn"] / 0.04])
    med = np.median([vec(c) for c in cands], axis=0)
    home = min(cands, key=lambda c: np.linalg.norm(vec(c) - med))
    near = [c for c in cands if abs(c["roll"] - home["roll"]) <= 15 and np.linalg.norm(c["center"] - home["center"]) <= 0.25 * iod]
    picked = [home]
    while len(picked) < count:
        best = max(near, key=lambda c: min(np.linalg.norm(vec(c) - vec(p)) for p in picked), default=None)
        if best is None or min(np.linalg.norm(vec(best) - vec(p)) for p in picked) < 1.0: break   # 剩下的都跟已挑的太像
        picked.append(best)
    return picked

def sheet(picked, names, dst):
    tiles = []
    for name, c in zip(names, picked):
        t = cv2.resize(c["img"], (480, round(480 * c["img"].shape[0] / c["img"].shape[1])), interpolation=cv2.INTER_AREA)
        cv2.putText(t, f"{name}  {c['sid']}#{c['n']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        tiles.append(t)
    cols = 3
    tiles += [np.zeros_like(tiles[0])] * (-len(tiles) % cols)
    cv2.imwrite(str(dst), np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 90])

if __name__ == "__main__":
    main()
