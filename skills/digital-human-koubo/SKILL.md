---
name: digital-human-koubo
description: 用固定的數位人形象（白背心數位人 / 使用者本人數位人 / 貓狗角色）做口播影片，先按內容推薦剪輯風格讓使用者選（小林式解說 / 網紅花字口播 / 發布解讀 / 保姆級教學 / 多主播多語言），自動套上從 MrBeast、MKBHD、影視颶風、Johnny Harris、Vox、半佛、差評等頂尖創作者拆出來的 48 個包裝元件（開場鉤子、數字釘子、文字在人身後的景深字、證據截圖、地圖路線、彈幕、投票、復盤板…），再寫稿 → 按 15 秒切段 → grok CLI（reference_to_video，Grok Imagine Video 1.5）分段生成（先報佔每週額度多少、使用者確認才生成）→ 逐段回聽 → 對齊 → Remotion 剪輯出片。觸發：用我的數位人講這段、數位人口播、讓白背心數位人說、用數位人 Skill、數位人帶貨 / 解讀 / 教學 / 種草影片、做成小林說那樣、加花字、加包裝 / 加地圖 / 加彈幕 / 開場加預告 / 文字放在人身後、做成 MrBeast 那種節奏、有哪些包裝手法。不用於：換一個全新形象（先按 references/new-avatar.md 做形象）、冒充真人。
---

# 數位人口播

形象、聲音、提示詞、切段規則固定在 `persona.json`；剪輯風格在 `references/style-menu.md`。每次照這裡做，出來的就是同一個人、同一種風格。

## 紅線
- 生成用的是使用者 grok 帳號的每週額度：跑 grok_generate.py 之前先報「段數 · 秒數 · 預估佔每週額度 X–Y%」，請使用者在 grok 裡輸入 /usage 看還剩多少，等使用者在對話裡明確同意。先拍第 1 段給使用者確認音色，再批次。重拍也要先報。
- grok 的影片工具在 ZDR（零資料保留）下不能用：要使用者自己在 grok 裡 /privacy 改成 Opt in。關著期間 grok 對話紀錄會上傳 xAI，做完提醒使用者改回 Opt out。不要替使用者改這個設定。
- 成品標「內容由 AI 數位人演繹」；場景、動物片段角上標「AI 生成」。
- 使用者本人的形象（persona.json → other_hosts.me）只用在使用者自己的片子裡。
- 「小林式」只學結構和剪輯手法：不用真實創作者的臉、聲音、佈景和原句。
- 點名評價第三方產品的說法，要有出處或標「網友分析 / 個人體驗」。展示素材只用使用者自己的作品；帶歌詞字幕的片子不用。

## 流程

### 準備：先檢查，有就跳過，缺才引導安裝（每次新對話第一次用時做）
**原則：已經裝好的一句話帶過，不讓使用者重新安裝；缺什麼才給裝法，裝法給多種，先放使用者當前用的那種。** 詳細裝法在 references/install.md。
1. **本機環境 + grok CLI**：`bash scripts/doctor.sh`。它查 grok 裝了沒、登入了沒，以及 ffmpeg、Python、Node、whisper。有的打 ✓ 不提；缺的它會按 macOS / Windows / Linux 列出多種裝法（詳見 references/install.md）。系統軟體讓使用者自己裝，Python 套件可以在使用者同意後幫裝。
2. **grok 裡的兩項設定**（只能使用者自己在 grok 互動介面看）：`/privacy` 要是 Opt in（ZDR 關著）；`/usage` 看本週額度還剩多少。請使用者確認後再往下。
3. **數位人形象**：persona.json 的 grok.reference_image（預設 assets/avatar_ref.jpg）在就直接用；要換形象 → 按 references/new-avatar.md 用使用者自己的照片。

### 0. 看內容 → 推薦風格 → 讓使用者選
按 `references/style-menu.md`：
1. 一行診斷（內容類型、有沒有可展示的素材、適合的平台和時長）。
2. 推薦 2 個風格並說理由，把 `assets/styles/` 裡對應的預覽圖發給使用者。
3. 一次問完：風格 · 比例和時長 · 花字強度（克制 / 標準 / 熱鬧）· 主播（白背心 / 使用者本人 / 兩人接力 / 動物）。每題第一個選項是推薦項。Claude Code 用 AskUserQuestion，其他工具列編號。
4. 使用者回「你定」就按推薦，並說一句按了什麼。結果寫進 `brief.json`，後面每一步按它來。

| 風格 | 比例 | 時長 | 剪輯實現 |
|---|---|---|---|
| A 小林式解說 | 16:9 | 3–20 分鐘 | finance-explainer skill 的引擎（episode.json 拍表） |
| B 網紅花字口播 | 9:16 | 30–120 秒 | `templates/huazi-916`（edit.json 驅動，三檔花字） |
| C 發布解讀 | 16:9 | 30–90 秒 | 參考實現 `templates/reference/launch-169` |
| D 保姆級教學 | 16:9 | 3–8 分鐘 | 參考實現 `templates/reference/tutorial-169` |
| E 多主播多語言 | 16:9 | 3–7 分鐘 | 參考實現 `templates/reference/multihost-169` |

### 1. 寫稿 → script.json
按選定風格的稿子寫法（style-menu.md 裡每種都有）。每段一句或兩句，10 秒左右（約 40–55 字，Grok 中文約 5.4 字/秒），標 `shot`：`full`（全螢幕出鏡）/ `pip`（畫中畫講解）/ `vlog`（隨意自拍口吻）/ `depth`（要做「文字在人身後」的段：中景、頭頂兩側留背景）。英文縮寫、網址寫成好唸的樣子。外語段直接寫目標語言的台詞。

### 2. 切段 + 報價
`python3 scripts/build_tasks.py script.json tasks.json --purpose "teaching a beginner tutorial step by step"`
→ 印出段數、秒數、預估佔 grok 每週額度的百分比（720p 實測每秒 0.25–0.35%）。full 段 720p，pip 段 480p（480p 沒實測，按 720p 估，偏高）。報給使用者等確認。使用者本人或動物主播用 persona.json → other_hosts 裡的提示詞模板和參考圖。

### 3. 生成
`python3 scripts/grok_generate.py tasks.json`：逐段調 grok CLI 的 reference_to_video，存成 `gen/<段 id>.mp4`，每段約 1–1.5 分鐘。已經存在的段跳過；重拍就刪掉那個檔案再跑，`--only s3` 只跑某段。
- 它只開放 reference_to_video 一個工具；grok 升級後多出新工具會在生成前中止，照提示把工具名補進腳本的 DISALLOWED。
- 報 ZDR 開著 → 請使用者在 grok 裡 /privacy 改成 Opt in 再跑。
- 標 ⚠ 的段是 grok 實際傳的參數和任務不一致，先看那段再決定要不要重拍。
- 要進場景（直播間、門店、街景）時，先用 grok 的 image_edit 合成開場畫面（人物參考圖 + 場景描述），存進工程後在 script.json 那幾段寫 `"ref": "圖片路徑"`，build_tasks.py 就會拿它當參考圖。

### 4. 回聽 + 抽幀 + 拼接
`python3 scripts/assemble.py script.json --out 成品_完整版.mp4`（讀 gen/<段 id>.mp4）：whisper 逐段轉寫比對文稿、只保留到說完後 0.25 秒、拼接、loudnorm -16。
- whisper `--prompt 原文` 會讓個別段漏掉前半句，用中性提示「以下是普通話的句子。」。外語段按語言轉寫；日韓阿拉伯語不要加 `-ml 1`（會把多位元組字元截斷成亂碼）。
- **每段抽 4 幀看一眼**：Grok 橫式口播偶爾自己燒字幕（提示詞寫了也擋不住），有就重拍那段。
- Grok 有時漏念開頭的語氣詞：沒影響意思就按實際口播改字幕，別為這個重拍。

### 5. 對齊 + 剪輯
`python3 scripts/align.py script.json --out <工程>/src/tl.json` 出逐字時間軸，然後按 brief.json 的風格剪：
- **B 花字口播**：`bash scripts/new_edit.sh huazi-916 <工程>` → 寫 `src/edit.json`（關鍵詞、表情、卡片、作品展示、號召，欄位見 references/huazi.md）→ `python3 scripts/check_edit.py <工程>/src` → 抽幀 → 渲染。
- **A 小林式**：`bash ~/.claude/skills/finance-explainer/scripts/setup_engine.sh <工程>`，按那邊的拍表和畫面語法做；數位人口播片段放進 host.json。
- **C / D / E**：`bash scripts/new_edit.sh reference/<目錄> <工程>`，換 tl.json，按段重寫 Scene（templates/reference/README.md）。
- **包裝（每種風格都做）**：按 `references/packaging-presets.json` 裡這個風格的預設包裝排——開場 30 秒按 open 順序、正文保證 stimulus_every_s 秒內有一個新視覺事件、講到 per_beat 裡那類內容就用對應元件、recurring 全片掛著。元件寫進 `pack` 陣列（欄位見 references/packaging.md），手法依據見 references/packaging-playbook.md。使用者點名要的手法（「加地圖」「開場加預告」「加彈幕」「換成 MrBeast 那種」）在預設基礎上加減。使用者問「有哪些包裝」先發 `assets/packaging/图鉴.jpg`。景深字（文字在人身後）要先跑 `scripts/cutout_video.py` 去背，見 references/packaging.md。
- 聲音：數位人影片軌一定 `muted`，人聲單獨鋪一條；多段 Grok 原聲用 `python3 scripts/voicefx/unify.py <輸出目錄> <片段…>` 統一頻譜 + 同一個小房間混響（複用舊段時加 `--ref 舊片段目錄`，場景/動物片段加 `--scene`）。BGM 壓在人聲下約 20 dB。
- 抽幀檢查一定看過渡的中間幀和零間隔銜接處（上一條的尾巴會蓋住下一條）。

## 參考
- references/install.md：grok CLI 和本機環境的多種裝法（只在缺的時候用）
- references/style-menu.md：五種風格、內容診斷、怎麼問使用者、brief.json
- references/packaging.md：47 個包裝元件的用法和參數（pack 寫法、9:16 自動適配）
- references/packaging-playbook.md：頂尖創作者實測結論（節奏、開場公式、字幕、聲音、號召、紅線），完整報告在 references/research/
- references/packaging-presets.json：五種風格各自的預設包裝
- references/huazi.md：花字模板 edit.json 欄位、九種卡片、三檔強度、寫法習慣
- persona.json：白背心數位人 + 其他主播（使用者本人、橘貓店長、柴犬主播）、提示詞模板、動作庫、多語言實測
- references/voice.md：換聲音（grok 內建音色 / MiMo 克隆 / 音色設計）
- references/new-avatar.md：從一張照片做新形象
- references/edit-styles.md：各剪輯工程的入口檔案和聲音統一做法
- assets/styles/：五種風格的預覽圖（給使用者選的時候發）
- assets/packaging/：包裝元件圖鑑（47 格總覽 + 每個元件一張）
