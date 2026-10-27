#!/usr/bin/env python3
"""tasks.json（build_tasks.py --backend comfy 生成）→ ComfyUI 上的 MiniMax H3 逐段生成口播片段 → gen/<段 id>.mp4。

用法：python3 comfy_generate.py tasks.json [--out gen] [--only s1,s3] [--url http://主机:8188] [--timeout 1200]
- 每段：参考图当第一帧，锁住这段的音轨（MiniMaxH3NativeAudioLock），H3 只生成画面、口型跟着音轨；片段的声音就是原音轨
- ComfyUI 地址：--url > 环境变量 COMFY_URL > persona.json 的 comfy.url；模型文件名、步数、尺寸也在 persona.json 的 comfy 那一节
- 前提：ComfyUI 有 MiniMax H3 原生节点和 ComfyUI-H3-NativeAudioLock 自定义节点，models 里有 persona.json 写的四个模型文件
- 第一帧先居中裁成目标比例再上传：H3 的节点会把第一帧直接拉伸成目标尺寸，不裁会变形
- 音轨先转成 48 kHz 立体声 wav（试拍验证过的格式）；帧数 = 音轨秒数 × 24，向上取到 H3 的 17k+5 格点，至少 124 帧
- 串行生成，576×1024 的 10 秒段约 3 分钟；gen/<id>.mp4 已存在且能解码就跳过，要重拍就删掉那个文件
- 不占 grok 额度，占的是那台机器的 GPU
"""
import hashlib, json, math, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
C = json.loads((HERE / "persona.json").read_text())["comfy"]

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def main():
    tasks = json.loads(Path(sys.argv[1]).read_text())
    if any("audio" not in t for t in tasks):
        sys.exit("这份 tasks.json 没有音轨，是 grok 后端的：用 build_tasks.py --backend comfy 重新生成")
    out = Path(arg("--out", "gen")); work = out / ".comfy"; work.mkdir(parents=True, exist_ok=True)
    only = set(arg("--only", "").split(",")) - {""}
    url = (arg("--url") or os.environ.get("COMFY_URL") or C["url"]).rstrip("/")
    timeout = int(arg("--timeout", "1200"))
    failed = []
    for t in tasks:
        if only and t["id"] not in only: continue
        dst = out / f"{t['id']}.mp4"
        if dst.exists() and decodes(dst):
            print(f"  {t['id']:5s} 已有 {dst}，跳过"); continue
        w, h = C["sizes"][t["aspect_ratio"]]
        img = upload(url, first_frame(t["images"][0], w, h, work / f"{t['id']}.jpg"))
        wav = upload(url, stereo_wav(t["audio"], work / f"{t['id']}.wav"))
        start = time.time()
        files, err = run(url, graph(t, img, wav, w, h), timeout)
        if err:
            failed.append(t["id"]); print(f"✗ {t['id']:5s} {err}"); continue
        download(url, files[0], dst)
        print(f"  {t['id']:5s} {duration(dst):.2f} 秒（生成 {time.time() - start:.0f} 秒）→ {dst}")
    print("跑完了。" + (f" 失败的段：{', '.join(failed)}" if failed else ""))
    sys.exit(1 if failed else 0)

def graph(t, img, wav, w, h):
    """ComfyUI API 格式的工作流：首帧图生视频 + 锁音轨，只对画面去噪。节点编号沿用 2026-10-27 试拍的工作流，方便对照。"""
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": C["unet"], "weight_dtype": "default"}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": C["clip"], "type": "minimax", "device": "default"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": C["video_vae"]}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": C["audio_vae"]}},
        "30": {"class_type": "LoadImage", "inputs": {"image": img}},
        "40": {"class_type": "LoadAudio", "inputs": {"audio": wav}},
        "7": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["4", 0], "vae": ["5", 0], "prompt": t["prompt"], "width": w, "height": h, "length": frames(t["duration"]), "first_frame": ["30", 0]}},
        "44": {"class_type": "MiniMaxH3NativeAudioLock", "inputs": {"model": ["1", 0], "av_latent": ["7", 1], "audio_vae": ["6", 0], "audio": ["40", 0]}},
        "8": {"class_type": "RandomNoise", "inputs": {"noise_seed": C["seed"]}},
        "9": {"class_type": "BasicGuider", "inputs": {"model": ["44", 0], "conditioning": ["7", 0]}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": C["sampler"]}},
        "11": {"class_type": "BasicScheduler", "inputs": {"model": ["1", 0], "scheduler": C["scheduler"], "steps": C["steps"], "denoise": 1.0}},
        "12": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["8", 0], "guider": ["9", 0], "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["44", 1]}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["5", 0]}},
        "15": {"class_type": "CreateVideo", "inputs": {"images": ["13", 0], "audio": ["44", 2], "fps": float(C["fps"])}},
        "16": {"class_type": "SaveVideo", "inputs": {"video": ["15", 0], "filename_prefix": f"koubo/{t['id']}", "format": "auto", "codec": "auto"}},
    }

def frames(sec):
    """音轨秒数 → H3 的帧数：向上取到 17k+5 格点，至少 124 帧（H3 训练范围约 124–362 帧）。音轨比画面短的部分是静音，assemble.py 会剪掉。"""
    n = math.ceil(sec * C["fps"])
    return max(124, 5 + 17 * math.ceil((n - 5) / 17))

def first_frame(src, w, h, dst):
    ffmpeg("-i", src, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}", "-q:v", "2", dst)
    return dst

def stereo_wav(src, dst):
    ffmpeg("-i", src, "-vn", "-ac", "2", "-ar", "48000", dst)
    return dst

def ffmpeg(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True)

def upload(url, path):
    """传进 ComfyUI 的 input 目录。文件名用内容哈希，同名一定同内容；回传 ComfyUI 实际存的名字。"""
    data = path.read_bytes()
    name = f"koubo_{hashlib.sha1(data).hexdigest()[:12]}{path.suffix}"
    b = uuid.uuid4().hex
    body = (f'--{b}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode() + data + f"\r\n--{b}--\r\n".encode()
    r = api(url, "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"})
    return f"{r['subfolder']}/{r['name']}" if r.get("subfolder") else r["name"]

def run(url, g, timeout):
    """提交一段并等它跑完，回传 (输出文件列表, 错误说明)。超时从提交算起，排队也算在内。"""
    pid = api(url, "/prompt", json.dumps({"prompt": g, "client_id": "digital-human-koubo"}).encode(), {"Content-Type": "application/json"})["prompt_id"]
    end = time.time() + timeout
    while time.time() < end:
        h = api(url, f"/history/{pid}").get(pid)   # 跑完（成功或出错）才会出现在 history 里
        if h:
            if h["status"]["status_str"] != "success":
                e = next((m[1] for m in h["status"]["messages"] if m[0] == "execution_error"), {})
                return None, f"{e.get('node_type', 'ComfyUI')} 出错：{e.get('exception_message', h['status'])}"
            return [f for o in h["outputs"].values() for f in o.get("images", [])], None
        time.sleep(5)
    return None, f"{timeout} 秒内没跑完（可能还在排队）；ComfyUI 那边不会自动取消，跑完的片段在它的 output/koubo/ 里"

def download(url, f, dst):
    q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f["subfolder"], "type": f["type"]})
    dst.write_bytes(api(url, f"/view?{q}", raw=True))

def api(url, path, body=None, headers=None, raw=False):
    req = urllib.request.Request(url + path, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:   # /prompt 的 400 里有 node_errors：缺模型、缺节点都在这里
        sys.exit(f"ComfyUI {path.split('?')[0]} 回 {e.code}：{e.read().decode(errors='replace')[:1500]}")
    except urllib.error.URLError as e:
        sys.exit(f"连不上 ComfyUI（{url}）：{e.reason}。确认那台机器开着、ComfyUI 带了 --listen，或用 --url / COMFY_URL 指定地址")
    return data if raw else json.loads(data)

def decodes(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    return r.returncode == 0 and not r.stderr.strip()

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out or 0)

if __name__ == "__main__":
    main()
