#!/usr/bin/env python3
"""生成后逐帧缩眼高：H3 会把眼睛画得比参考图圆，改输入（缩小参考图的眼睛、换权重、修脸节点）都压不住，所以在输出上修。
用法：uv run --no-project --with mediapipe --with opencv-python-headless python scripts/warp_eyes.py <输入.mp4> <输出.mp4> [倍率，默认 persona.json 的 comfy.eye_warp]
- 只压垂直方向（H3 的眼宽本来就和参考图一样，多出来的是眼高），以两眼中心为圆心的椭圆范围内中心缩成「倍率」倍、到边缘平滑回到 1，嘴和其他地方不动
- 每帧找两眼中心和眼宽，前后 5 帧取中位数再变形，眼睛不会抖；找不到脸的帧沿用上一帧
- 直接在 YUV 三个平面上变形，椭圆外的像素一个值都不变。不要先转 RGB：ffmpeg 转回 YUV 时整片 Y 平均会偏 0.5–2.3
- 原始画面送回 ffmpeg 前用 setparams 标上来源的色彩参数，不然 ffmpeg 9 会当成 bt601 再自动转成 bt709，整片变暗约 2
- assemble.py 拼完 comfy 段会自动跑这个；声音原样复制"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # uv run python -I 不会把脚本目录放进 sys.path
import cv2, numpy as np
import face

def main():
    src, dst = sys.argv[1], sys.argv[2]
    s = float(sys.argv[3]) if len(sys.argv) > 3 else json.loads((Path(__file__).resolve().parent.parent / "persona.json").read_text())["comfy"]["eye_warp"]
    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                    "stream=width,height,r_frame_rate,color_space,color_primaries,color_transfer,color_range", "-of", "json", src],
                                   capture_output=True, text=True, check=True).stdout)["streams"][0]
    W, H = st["width"], st["height"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, H * 3 // 2, W)
    eyes = smoothed_eyes(frames)
    params = ":".join(f"{p}={st[k]}" for k, p in (("color_space", "colorspace"), ("color_primaries", "color_primaries"),
                                                    ("color_transfer", "color_trc"), ("color_range", "range")) if st.get(k) and st[k] != "unknown")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}", "-r", st["r_frame_rate"], "-i", "-",
                           "-i", src, "-map", "0:v", "-map", "1:a?", *(["-vf", f"setparams={params}"] if params else []),
                           "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    for f, g in zip(frames, eyes):
        Y, U, V = f[:H], f[H:H + H // 4].reshape(H // 2, W // 2), f[H + H // 4:].reshape(H // 2, W // 2)
        planes = [cv2.remap(Y, *vertical_map(W, H, g, s, 1.0), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)]
        cm = vertical_map(W // 2, H // 2, g, s, 0.5)
        planes += [cv2.remap(p, *cm, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT) for p in (U, V)]
        ff.stdin.write(b"".join(p.tobytes() for p in planes))
    ff.stdin.close()
    if ff.wait(): sys.exit(f"ffmpeg 写 {dst} 失败")

def smoothed_eyes(frames):
    """每帧两只眼的 (中心 x, 中心 y, 眼宽)，前后 5 帧取中位数；开头找不到脸就用第一个找到的"""
    geo, last = [], None
    for f in frames:
        pts = face.landmarks(cv2.cvtColor(f, cv2.COLOR_YUV2BGR_I420))   # 只用来找关键点，不写回
        if pts is not None: last = [(*e["center"], e["width"]) for e in face.eye_geometry(pts)]
        geo.append(last)
    first = next((g for g in geo if g), None)
    if first is None: sys.exit("整段都找不到脸")
    geo = np.array([g or first for g in geo])
    return np.array([np.median(geo[max(0, i - 2):i + 3], axis=0) for i in range(len(geo))])

def vertical_map(w, h, eyes, s, scale):
    """垂直缩放的取样坐标：椭圆横 1.25 倍、纵 0.75 倍眼宽（盖到眼角外、不碰眉毛）；scale = 这个平面相对于 Y 的大小"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    my = yy.copy()
    for cx, cy, ew in eyes:
        cx, cy, ew = cx * scale, cy * scale, ew * scale
        dx, dy = xx - cx, yy - cy
        t = np.clip(np.sqrt((dx / (1.25 * ew)) ** 2 + (dy / (0.75 * ew)) ** 2), 0, 1)
        k = s + (1 - s) * (t * t * (3 - 2 * t))
        inside = t < 1
        my[inside] = (cy + dy / k)[inside]
    return xx, my

if __name__ == "__main__":
    main()
