# 安裝引導（只在缺的時候用）

原則：**已經有的一句話帶過，不提安裝**；缺什麼才給裝法。裝法給多種：先放使用者當前在用的那種（標「推薦」），其餘列在下面讓使用者挑。裝完再檢查一次確認。

## 1. grok CLI（生成數位人片段）

### 怎麼判斷有沒有
`bash scripts/doctor.sh` 會查 grok 裝了沒、登入了沒。另外兩項只能請使用者在 grok 互動介面裡看：
- `/privacy`：要是 **Opt in**（ZDR 關著），由使用者自己在 grok 裡改，不要替使用者改。ZDR 開著時影片工具直接報「unavailable under zero data retention」。關著期間 grok 對話紀錄會上傳 xAI，做完提醒使用者改回 Opt out。
- `/usage`：本週額度還剩多少。720p 實測每秒約佔 0.25–0.35%（2026-10-26，X Premium+）。

### 裝法
| 系統 | 命令 |
|---|---|
| **macOS / Linux / WSL** | `curl -fsSL https://x.ai/cli/install.sh \| bash` |
| **Windows（PowerShell）** | `irm https://x.ai/cli/install.ps1 \| iex` |

裝完執行 `grok login`，在瀏覽器登入 grok 帳號。2026-10-26 實測 X Premium+ 帳號能用影片工具，其他方案沒測過。

### 想讓 ZDR 一直開著？
官方文件寫可以在 `managed_config.toml` 配一個 S3 儲存桶（`tools.zdr_video_output_s3`），讓 ZDR 開著也能生成。但 2026-10-26 用個人帳號（grok 1.0.70）實測都不生效：`~/.grok/managed_config.toml` 每次啟動被 grok 刪掉，寫在 `~/.grok/config.toml` 或 `/etc/grok/managed_config.toml` 也照樣報 ZDR 錯誤。目前只能生成時關掉 ZDR。

## 2. 本機環境（剪輯時才需要）
`bash scripts/doctor.sh` 會逐項檢查：有的打 ✓ 跳過，缺的才列出多種裝法。**系統軟體讓使用者自己裝，不要替使用者執行安裝命令**（Python 套件可以在使用者同意後幫裝）。

| 缺的 | macOS | Windows | Linux | 其他 |
|---|---|---|---|---|
| ffmpeg | `brew install ffmpeg` | `winget install Gyan.FFmpeg` 或 `choco install ffmpeg` | `sudo apt install ffmpeg` | 官網 ffmpeg.org 下載 |
| Python 3 | `brew install python` | `winget install Python.Python.3.12` | `sudo apt install python3 python3-pip` | python.org 下載；或 conda |
| numpy / Pillow | `python3 -m pip install numpy pillow` | 同左 | 同左 | `conda install numpy pillow` |
| Node 18+ | `brew install node` | `winget install OpenJS.NodeJS.LTS` | `sudo apt install nodejs npm` 或 nvm | nodejs.org 下載；`nvm install --lts` |
| whisper-cli | `brew install whisper-cpp` | 從 github.com/ggerganov/whisper.cpp Releases 下載 | 原始碼編譯（`cmake -B build && cmake --build build`） | — |
| whisper 模型 | 下載 `ggml-medium-q5_0.bin`（huggingface.co/ggerganov/whisper.cpp）放到 `~/models/` | 同左 | 同左 | 或 `export WHISPER_MODEL=模型路徑` |
| opencc（可選，稿子寫繁體時 assemble.py 比對用） | `brew install opencc` | 見 github.com/BYVoid/OpenCC | `sudo apt install opencc` | — |

Remotion 不用單獨裝：`scripts/new_edit.sh` 起工程時會先從本機已有的 Remotion 工程克隆，沒有才 `npm install`；npm 源連不上時換鏡像 `npm config set registry https://registry.npmmirror.com`。

## 3. 數位人形象
persona.json 的 grok.reference_image（預設 assets/avatar_ref.jpg）檔案在 → 直接用。要換形象 → 按 references/new-avatar.md 用使用者自己的照片。
