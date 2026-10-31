#!/usr/bin/env bash
# 在 Colab VM 上装 ComfyUI（钉 $COMMIT）、按 /content/dl.txt 下载模型、装 /content/nodes/ 里的自定义节点、启动 ComfyUI（只听 127.0.0.1，给 SSH 通道用）。
# colab_h3.py 经 ssh 送进来跑。重复跑是安全的：装过的步骤跳过，模型已有的不重下，ComfyUI 已在跑就只做检查。
# 环境变量：COMMIT（必填，ComfyUI 的 commit sha）、LAUNCH_ARGS（ComfyUI 启动参数，默认 --highvram --disable-mmap）
set -uo pipefail
T0=$(date +%s); log() { echo "[$(( $(date +%s) - T0 ))s] $*"; }
COMMIT=${COMMIT:?需要 COMMIT}; LAUNCH_ARGS=${LAUNCH_ARGS:---highvram --disable-mmap}
C=/content/ComfyUI; M=$C/models
log "env: $(python3 --version 2>&1) | $(python3 -c 'import torch;print("torch",torch.__version__,"cuda",torch.version.cuda)' 2>&1) | $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1)"

# 1. ComfyUI：只抓那一个 commit（GitHub 允许按 sha fetch；不行就整个 clone）
if [ ! -f $C/main.py ]; then
  mkdir -p $C && cd $C && git init -q && git remote add origin https://github.com/comfyanonymous/ComfyUI.git
  git fetch -q --depth 1 origin "$COMMIT" || { log "按 sha 抓不到，改整个 clone"; cd /content && rm -rf ComfyUI && git clone -q --filter=blob:none https://github.com/comfyanonymous/ComfyUI.git && cd ComfyUI && git fetch -q origin "$COMMIT"; }
  git checkout -q FETCH_HEAD
fi
cd $C && log "ComfyUI $(git rev-parse --short HEAD)"

# 2. 模型在后台下载（最花时间），pip 跟它并行。已经完整的文件从清单里拿掉，不然 aria2c 会另存成 .1
command -v aria2c > /dev/null || apt-get install -y -qq aria2 > /dev/null 2>&1 || { apt-get update -qq > /dev/null 2>&1 && apt-get install -y -qq aria2 > /dev/null 2>&1; }
python3 - <<'PY'
import os, re
blocks = re.split(r"\n(?=\S)", open("/content/dl.txt").read().strip())
keep = []
for b in blocks:
    d = re.search(r"dir=(\S+)", b); o = re.search(r"out=(\S+)", b)
    p = os.path.join(d.group(1), o.group(1))
    if os.path.exists(p) and os.path.getsize(p) > 0 and not os.path.exists(p + ".aria2"): print("已有", o.group(1)); continue
    os.makedirs(d.group(1), exist_ok=True); keep.append(b)
open("/content/dl.todo.txt", "w").write("\n".join(keep) + ("\n" if keep else ""))
PY
TDL=$(date +%s); DLPID=
if [ -s /content/dl.todo.txt ]; then
  aria2c -i /content/dl.todo.txt -j4 -x16 -s16 -k16M --file-allocation=none --continue=true --console-log-level=warn --summary-interval=0 > /content/aria2.log 2>&1 &
  DLPID=$!; log "模型开始下载"
fi
# 3. 相依套件（Colab 自带的 torch 不重装）
if [ ! -f /content/.pip_done ]; then
  pip install -q -r requirements.txt > /content/pip.log 2>&1 && touch /content/.pip_done && log "pip 装好" || { log "pip 失败"; tail -20 /content/pip.log; exit 1; }
fi
# 4. 自定义节点：/content/nodes/<目录> → custom_nodes/<目录>
if [ -d /content/nodes ]; then
  for d in /content/nodes/*/; do n=$(basename "$d"); rm -rf "custom_nodes/$n"; cp -r "$d" "custom_nodes/$n"; log "节点 $n"; done
fi
# 5. 等下载
if [ -n "$DLPID" ]; then
  wait $DLPID; RC=$?; DT=$(( $(date +%s) - TDL )); GB=$(du -sb $M | cut -f1)
  log "模型下载 rc=$RC，共 $(( GB / 1000000000 )) GB，$DT 秒，约 $(( GB / 1000000 / (DT + 1) )) MB/s"
  [ $RC -eq 0 ] || { tail -20 /content/aria2.log; exit 1; }
fi
# 6. 启动 ComfyUI
if ! curl -s -m 3 http://127.0.0.1:8188/system_stats > /dev/null; then
  nohup python3 main.py --listen 127.0.0.1 --port 8188 $LAUNCH_ARGS > /content/comfyui.log 2>&1 &
  for i in $(seq 60); do curl -s -m 3 http://127.0.0.1:8188/system_stats > /dev/null && break; sleep 3; done
fi
curl -s -m 5 http://127.0.0.1:8188/system_stats > /dev/null || { log "ComfyUI 没起来"; tail -30 /content/comfyui.log; exit 1; }
grep -iE "import failed|Traceback" /content/comfyui.log | head -5
log "READY"
