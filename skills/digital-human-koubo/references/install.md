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

## 3. 数字人形象
persona.json 的 grok.reference_image（默认 assets/avatar_ref.jpg）文件在 → 直接用。要换形象 → 按 references/new-avatar.md 用用户自己的照片。
