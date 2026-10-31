# 安装引导（只在缺的时候用）

原则：**已经有的一句话带过，不提安装**；缺什么才给装法。装法给多种：先放用户当前在用的那种（标「推荐」），其余列在下面让用户挑。装完再检查一次确认。

## 1. grok CLI（生成数字人片段）

### 怎么判断有没有
`bash scripts/doctor.sh` 会查 grok 装了没、登录了没。另外两项只能请用户在 grok 交互界面里看：
- `/privacy`：要是 **Opt in**（ZDR 关着），由用户自己在 grok 里改，不要替用户改。ZDR 开着时视频工具直接报「unavailable under zero data retention」。关着期间 grok 会话记录会上传 xAI，做完提醒用户改回 Opt out。
- `/usage`：本周额度还剩多少。720p 实测每秒约占 0.25–0.35%（2026-10-26，X Premium+）。

### 装法
| 系统 | 命令 |
|---|---|
| **macOS / Linux / WSL** | `curl -fsSL https://x.ai/cli/install.sh \| bash` |
| **Windows（PowerShell）** | `irm https://x.ai/cli/install.ps1 \| iex` |

装完运行 `grok login`，在浏览器登录 grok 账号。2026-10-26 实测 X Premium+ 账号能用视频工具，其他方案没测过。

### 想让 ZDR 一直开着？
官方文档写可以在 `managed_config.toml` 配一个 S3 储存桶（`tools.zdr_video_output_s3`），让 ZDR 开着也能生成。但 2026-10-26 用个人账号（grok 1.0.70）实测都不生效：`~/.grok/managed_config.toml` 每次启动被 grok 删掉，写在 `~/.grok/config.toml` 或 `/etc/grok/managed_config.toml` 也照样报 ZDR 错误。目前只能生成时关掉 ZDR。

## 2. 本机环境（剪辑时才需要）
`bash scripts/doctor.sh` 会逐项检查：有的打 ✓ 跳过，缺的才列出多种装法。**系统软件让用户自己装，不要替用户执行安装命令**（Python 包可以在用户同意后帮装）。

| 缺的 | macOS | Windows | Linux | 其他 |
|---|---|---|---|---|
| ffmpeg | `brew install ffmpeg` | `winget install Gyan.FFmpeg` 或 `choco install ffmpeg` | `sudo apt install ffmpeg` | 官网 ffmpeg.org 下载 |
| Python 3 | `brew install python` | `winget install Python.Python.3.12` | `sudo apt install python3 python3-pip` | python.org 下载；或 conda |
| numpy / Pillow | `python3 -m pip install numpy pillow` | 同左 | 同左 | `conda install numpy pillow` |
| Node 18+ | `brew install node` | `winget install OpenJS.NodeJS.LTS` | `sudo apt install nodejs npm` 或 nvm | nodejs.org 下载；`nvm install --lts` |
| whisper-cli | `brew install whisper-cpp` | 从 github.com/ggerganov/whisper.cpp Releases 下载 | 源码编译（`cmake -B build && cmake --build build`） | — |
| whisper 模型 | 下载 `ggml-medium-q5_0.bin`（huggingface.co/ggerganov/whisper.cpp）放到 `~/models/` | 同左 | 同左 | 或 `export WHISPER_MODEL=模型路径` |
| opencc（可选，稿子写繁体时 assemble.py 比对用） | `brew install opencc` | 见 github.com/BYVoid/OpenCC | `sudo apt install opencc` | — |

Remotion 不用单独装：`scripts/new_edit.sh` 起工程时会先从本机已有的 Remotion 工程克隆，没有才 `npm install`；npm 源连不上时换镜像 `npm config set registry https://registry.npmmirror.com`。

## 3. CosyVoice 3（comfy 后端配音用，装在 GPU 机器上）
tts_generate.py 经 ssh 调用，所以要能免密码 ssh 到那台机器（`ssh 主机名 true` 不问密码）。2026-10-29 在 Ubuntu + RTX 3090 Ti 装好的做法：
1. `git clone --recursive https://github.com/QwenAudio/CosyVoice`（Matcha-TTS 是子模块，要一起抓）。
2. `uv venv --python 3.10`，再装 `requirements.txt`，去掉 deepspeed、gradio、onnxruntime（CPU 版）和三个 tensorrt 包，只做推理用不到。torch 是 2.3.1 + cu121。
3. `hf download FunAudioLLM/Fun-CosyVoice3-0.5B-2512 --local-dir pretrained_models/Fun-CosyVoice3-0.5B`，在 repo 目录里跑。
4. 把 python、repo、模型路径填进 persona.json 的 tts 那一节；gpu_lock 是任意一个锁文件路径，flock 会自己建。
- wetext 从 modelscope 下载失败（HTTP 403）时只会用内置的基本文字正规化，试听结果不受影响。

## 4. Google Colab G4（可选，没有自己的 GPU 时跑 comfy 后端）
1. `uv tool install google-colab-cli`，在自己的终端跑 `colab usage`：它印出一个网址，浏览器登录有 Colab 算力的 Google 账号、把代码贴回去。只做一次，之后 scripts/colab_h3.py 直接用。
2. 要有 `~/.ssh/id_ed25519`（colab ssh 只收 ed25519 / ecdsa）。
3. 把 ComfyUI 的自定义节点 `ComfyUI-H3-NativeAudioLock/`（目前没有 git 来源，从自己跑 H3 的 ComfyUI 的 custom_nodes/ 复制）放到 `assets/colab_nodes/ComfyUI-H3-NativeAudioLock/__init__.py`。这个目录不进仓库。
4. persona.json 的 comfy.colab 写 ComfyUI 的 commit、模型下载地址（HF 公开地址）、启动参数。换模型时四个文件名都要有地址。
- 费用：G4 每小时约 10 CCU（2026-10-31 实测 10.05）；开机加装环境约 3 分钟，之后每段 1024×576 约 45 秒。
- 一台 runtime 同时只能有一条 colab ssh；看守进程到 max_minutes 会强制 colab stop，跑长片先调高。

## 5. 数字人形象
persona.json 的 grok.reference_image（默认 assets/avatar_ref.jpg）文件在 → 直接用。要换形象 → 按 references/new-avatar.md 用用户自己的照片。
