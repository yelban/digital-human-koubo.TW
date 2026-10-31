#!/usr/bin/env python3
"""没有自己的 GPU 时，在 Google Colab 的 G4（RTX PRO 6000，96 GB）上跑 comfy 后端：开机、接 SSH 通道、装 ComfyUI 和模型、生成、关机，一条命令做完，带账单防呆。
用法：python3 colab_h3.py tasks.json [comfy_generate.py 的参数：--out gen --only n1,n3 --timeout 1500 --no-anchors] [--session h3] [--keep] [--max-minutes 30] [--port 18188]
- 事前：`uv tool install google-colab-cli`，在自己的终端跑一次 `colab usage` 完成 OAuth 登录；~/.ssh/id_ed25519 要存在（colab ssh 用它）。
- 设置在 persona.json 的 comfy.colab：gpu、ComfyUI 的 commit、模型下载地址、启动参数、session 名、max_minutes。
- 自定义节点放 assets/colab_nodes/<节点目录>/，整个目录传到 VM 的 custom_nodes/。NativeAudioLock 从自己的 ComfyUI 复制过来，不进仓库。
- 账单防呆三层：
  1. 看守进程：另起一个独立进程，到 max_minutes 就 colab stop。主进程被杀、Mac 合盖都不影响它。
  2. 主进程不管成功、报错还是 Ctrl-C，最后都 colab stop（--keep 除外），再读 colab usage 确认 Active assignments: 0，打印这次用了多少 CCU。
  3. comfy_generate.py 自己的 --timeout。
- --keep：跑完不关机，下一次同名 session 直接复用，省掉约 3 分钟安装。看守进程照样在 max_minutes 关机。
- 同一台 runtime 只能有一条 colab ssh（第二条回 429），所以通道和远程命令共用一条 ControlMaster 连接。
- 花 CCU 前先把预估（约 0.5 CCU 开机 + 每段约 0.15 CCU，费率 10 CCU/h）报给用户，跟 grok 额度一样等确认。
- 2026-10-31 实测：开机 4 秒，装 ComfyUI 加下载 42 GB 模型 169 秒（HF 约 300 MB/s），1024×576 一段 43–47 秒，费率 10.05 CCU/h。"""
import io, json, re, shutil, subprocess, sys, tarfile, tempfile, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
C = json.loads((SKILL / "persona.json").read_text())["comfy"]
CL = C["colab"]
COLAB = shutil.which("colab") or str(Path.home() / ".local/bin/colab")
OWN_FLAGS = {"--session": 1, "--keep": 0, "--max-minutes": 1, "--port": 1}

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    tasks = Path(sys.argv[1])
    session = arg("--session", CL.get("session", "h3")); port = int(arg("--port", "18188"))
    max_min = float(arg("--max-minutes", CL.get("max_minutes", 30))); keep = "--keep" in sys.argv
    passthrough = []
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] in OWN_FLAGS: i += 1 + OWN_FLAGS[sys.argv[i]]; continue
        passthrough.append(sys.argv[i]); i += 1
    out = Path(arg("--out", "gen")); out.mkdir(parents=True, exist_ok=True)
    host = f"root@colab-{session}"; sock = Path(tempfile.gettempdir()) / f"colab-{session}.sock"
    nodes = SKILL / "assets" / "colab_nodes"
    if not (nodes / "ComfyUI-H3-NativeAudioLock" / "__init__.py").exists():
        sys.exit(f"缺 {nodes}/ComfyUI-H3-NativeAudioLock/__init__.py：从自己的 ComfyUI 的 custom_nodes/ 复制过来（见 references/install.md）")
    t0 = time.time(); bal0, rate0, _ = usage()
    log(f"余额 {bal0} CCU；看守上限 {max_min:g} 分钟")
    if session_exists(session):
        log(f"session {session} 已经在跑，直接复用")
    else:
        log(f"开 {CL['gpu']}：colab new -s {session} --gpu {CL['gpu']}")
        colab("new", "-s", session, "--gpu", CL["gpu"])
    guard_log = out / ".comfy" / "colab_guard.log"; guard_log.parent.mkdir(parents=True, exist_ok=True)
    guard = subprocess.Popen([sys.executable, __file__, "--guard", session, str(t0 + max_min * 60)],
                             stdout=open(guard_log, "a"), stderr=subprocess.STDOUT, start_new_session=True)
    rc = 1
    try:
        tunnel(sock, host, session, port)
        if comfy_ready(port):
            log("ComfyUI 已经在跑，跳过安装")
        else:
            setup(sock, host, nodes)
        preflight(port)
        cmd = [sys.executable, str(HERE / "comfy_generate.py"), str(tasks), *passthrough, "--url", f"http://127.0.0.1:{port}"]
        log("生成：" + " ".join(cmd[1:]))
        rc = subprocess.run(cmd).returncode
    finally:
        subprocess.run(["ssh", "-S", str(sock), "-O", "exit", host], capture_output=True)
        if keep:
            log(f"--keep：{session} 还开着（每小时约 {rate0 or 10} CCU），看守进程会在 {max_min:g} 分钟时关机；手动关：colab stop -s {session}")
        else:
            log(f"关机：colab stop -s {session}"); colab("stop", "-s", session, check=False)
            guard.terminate()
        bal1, rate1, active = usage()
        mins = (time.time() - t0) / 60
        log(f"用时 {mins:.1f} 分钟，余额 {bal0} → {bal1} CCU（扣 {bal0 - bal1:.2f}；colab usage 有时延迟入账），当前 {active} 台在跑、{rate1}/hr")
        if not keep and active:
            log("警告：还有机器在跑，再停一次"); colab("stop", "-s", session, check=False)
    sys.exit(rc)

def guard(session, deadline):
    """独立进程：到点还活着就强制关机"""
    while time.time() < deadline:
        time.sleep(min(30, max(1, deadline - time.time())))
    if session_exists(session):
        log(f"看守：到上限，强制 colab stop -s {session}"); colab("stop", "-s", session, check=False)
    log("看守：" + colab("usage", check=False).replace("\n", " | "))

def colab(*args, check=True):
    r = subprocess.run([COLAB, *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if check and r.returncode:
        sys.exit(f"colab {' '.join(args)} 失败：{out[-600:]}（没登录过先在自己的终端跑 colab usage）")
    return out

def usage():
    out = colab("usage")
    m = lambda p: re.search(p, out)
    return (float(m(r"balance:\s*([\d.]+)").group(1)) if m(r"balance:\s*([\d.]+)") else None,
            float(m(r"rate:\s*([\d.]+)").group(1)) if m(r"rate:\s*([\d.]+)") else None,
            int(m(r"assignments:\s*(\d+)").group(1)) if m(r"assignments:\s*(\d+)") else None)

def session_exists(session):
    return "not found" not in colab("status", "-s", session, check=False)

def tunnel(sock, host, session, port):
    """ControlMaster 主连接 + 本机 port → VM 8188；旧的还能用就沿用"""
    if sock.exists():
        if subprocess.run(["ssh", "-S", str(sock), "-O", "check", host], capture_output=True).returncode == 0: return
        sock.unlink()
    cmd = ["ssh", "-f", "-N", "-M", "-S", str(sock), "-o", "ExitOnForwardFailure=yes", "-o", "StrictHostKeyChecking=no",
           "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=ERROR", "-o", "ServerAliveInterval=30",
           "-o", f"ProxyCommand={COLAB} ssh --proxy-mode -s {session}", "-L", f"{port}:127.0.0.1:8188", host]
    err_log = sock.with_suffix(".log")
    for _ in range(4):   # 刚开机 sshd 可能还没好
        # stderr 不能接 pipe：ProxyCommand 子进程跟主连接活一样久，会一直握着它，run() 就等不到 EOF
        with open(err_log, "w") as err:
            r = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=err)
        if r.returncode == 0 and subprocess.run(["ssh", "-S", str(sock), "-O", "check", host], capture_output=True).returncode == 0:
            log(f"SSH 通道 127.0.0.1:{port} → VM 8188"); return
        log(f"通道没接上（{err_log.read_text().strip()[-200:]}），10 秒后重试"); time.sleep(10)
    sys.exit("SSH 通道接不上。本机 18188 被占用就换 --port；另一条 colab ssh 还连着就先断掉")

def ssh(sock, host, remote_cmd, stdin=None):
    r = subprocess.run(["ssh", "-S", str(sock), "-o", "LogLevel=ERROR", host, remote_cmd], input=stdin, capture_output=True)
    if r.returncode: sys.exit(f"VM 上执行失败：{remote_cmd[:80]} → {r.stderr.decode(errors='replace')[-400:]}")
    return r.stdout

def setup(sock, host, nodes):
    """传下载清单和节点，跑 remote/colab_setup_h3.sh，边跑边印"""
    dl = "".join(f"{url}\n  dir=/content/ComfyUI/models/{Path(rel).parent}\n  out={Path(rel).name}\n" for rel, url in CL["models"].items())
    ssh(sock, host, "cat > /content/dl.txt", dl.encode())
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for d in nodes.iterdir():
            if d.is_dir(): tar.add(d, arcname=d.name)
    ssh(sock, host, "rm -rf /content/nodes && mkdir -p /content/nodes && tar xzf - -C /content/nodes", buf.getvalue())
    env = f"COMMIT={CL['comfyui_commit']} LAUNCH_ARGS='{' '.join(CL.get('launch_args', []))}'"
    log(f"安装 ComfyUI {CL['comfyui_commit'][:8]} + {len(CL['models'])} 个模型（第一次约 3 分钟）")
    p = subprocess.Popen(["ssh", "-S", str(sock), "-o", "LogLevel=ERROR", host, f"{env} bash -s"],
                         stdin=open(HERE / "remote" / "colab_setup_h3.sh", "rb"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = ""
    for line in p.stdout:
        last = line.rstrip(); print("  VM " + last, flush=True)
    if p.wait() or not last.endswith("READY"): sys.exit("VM 安装没成功，看上面 VM 的输出；机器还开着，修好后重跑会接着做")

def comfy_ready(port):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/system_stats", timeout=3); return True
    except Exception:
        return False

def preflight(port):
    """确认 persona 指定的模型文件名 ComfyUI 都看得到"""
    want = {"UNETLoader": ("unet_name", C["unet"]), "CLIPLoader": ("clip_name", C["clip"]), "VAELoader": ("vae_name", C["video_vae"])}
    for node, (field, name) in want.items():
        info = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/object_info/{node}", timeout=10).read())
        have = info[node]["input"]["required"][field][0]
        if name not in have: sys.exit(f"VM 的 ComfyUI 没有 {name}（有：{have}）。persona.json 的 comfy.colab.models 要有这个文件的下载地址")
    info = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/object_info/VAELoader", timeout=10).read())
    if C["audio_vae"] not in info["VAELoader"]["input"]["required"]["vae_name"][0]: sys.exit(f"VM 的 ComfyUI 没有 {C['audio_vae']}")
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/object_info/MiniMaxH3NativeAudioLock", timeout=10).read()
    except Exception:
        sys.exit("VM 的 ComfyUI 没载入 MiniMaxH3NativeAudioLock，看 VM 的 /content/comfyui.log")
    log("模型和节点都在")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--guard":
        guard(sys.argv[2], float(sys.argv[3]))
    elif len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        sys.exit(__doc__)
    else:
        main()
