<div align="center">

# Digital Human Koubo · AI 數位人口播

**一張照片 + 一句話 → 一條帶數位人出鏡的口播成品。**
寫稿、對口型的 AI 主播、修音、字幕、頂尖創作者級包裝，全部交給你的 AI Agent 自動完成。

[English](README.md) · [简体中文](README.zh-CN.md) · **繁體中文**

> 這是 [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo) 的繁體中文版，影片生成改用 grok CLI。內容由 `tools/zhtw/zhtw.py` 從 `simplified` 分支自動轉換。

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-orange)
![grok CLI](https://img.shields.io/badge/video-grok%20CLI-000000)
![Remotion](https://img.shields.io/badge/edit-Remotion%204-0b84f3)

<img src="docs/images/cover.jpg" width="820" alt="一張照片 + 一句話，27 秒直播帶貨廣告">

</div>

> 這條 27 秒的直播間廣告裡，主播不存在。臉、聲音、直播間、花字、價格動畫，全是 AI 做的。
> 輸入只有一句話：「用這個數位人做一條 30 秒直播間廣告，賣 WorkBuddy 上手課，10 節課 99 元，原價 999。」
> 這條示例當時是用 Renoise 生成的（482 積分）。現在的流程改用 grok CLI，用的是你 grok 帳號的每週額度，見「成本參考」。

---

## 示例

點 GIF 或「播放」看完整影片。下面每一條都是用這個倉庫做出來的。

| | | |
|:---:|:---:|:---:|
| <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/workbuddy-live-ad.mp4"><img src="docs/gifs/workbuddy-live-ad.gif" width="230"></a> | <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/renoise-koubo-huazi.mp4"><img src="docs/gifs/renoise-koubo-huazi.gif" width="230"></a> | <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/text-behind.mp4"><img src="docs/gifs/text-behind.gif" width="300"></a> |
| **直播間帶貨廣告** · 9:16 · 27 秒<br>風格 B + 景深價格 ¥999→¥99<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/workbuddy-live-ad.mp4) | **產品推薦口播** · 9:16 · 89 秒<br>花字、動態表情、畫中畫<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/renoise-koubo-huazi.mp4) | **文字在人身後（景深字）** · 5 秒<br>Vision 人像去背，三層合成<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/text-behind.mp4) |

| | |
|:---:|:---:|
| <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/tutorial-ep2.mp4"><img src="docs/gifs/tutorial-ep2.gif" width="400"></a> | <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/tutorial-digital-human-upgrade.mp4"><img src="docs/gifs/tutorial-digital-human-upgrade.gif" width="400"></a> |
| **保姆級教學** · 16:9 · 4 分 36 秒<br>數位人親自講「我是怎麼被做出來的」（風格 D）<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/tutorial-ep2.mp4) | **數位人升級版** · 16:9 · 5 分 55 秒<br>兩位主播、六種語言、四個場景、貓狗角色（風格 E）<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/tutorial-digital-human-upgrade.mp4) |
| <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/memt-launch.mp4"><img src="docs/gifs/memt-launch.gif" width="400"></a> | <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/xiaolin-style-explainer.mp4"><img src="docs/gifs/xiaolin-style-explainer.gif" width="400"></a> |
| **發布解讀** · 16:9 · 39 秒<br>主播在側邊，右側程式碼動效（風格 C）<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/memt-launch.mp4) | **財經 / 科技解說** · 16:9 · 2 分 21 秒<br>圖表、檔案標黃、章節卡（風格 A）<br>[▶ 播放](https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/xiaolin-style-explainer.mp4) |

<div align="center">
<a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/packaging-gallery.mp4"><img src="docs/gifs/packaging-gallery.gif" width="560"></a><br>
<b>包裝元件圖鑑</b> · 48 個元件 · 2 分 40 秒 · <a href="https://github.com/andyhuo520/digital-human-koubo/releases/download/v1.0.0/packaging-gallery.mp4">▶ 播放</a>
</div>

> 示例裡的主播全部是 AI 數位人，每條片子都標了「內容由 AI 數位人演繹」。男主播是作者用本人照片做的數字分身。

---

## 能做什麼

- **一張照片做出固定的數位人**：臉、服裝、聲音描述、提示詞模板都存在 `persona.json`，每條片子都是同一個人。想進什麼場景（直播間、門店、教室、京都街頭），先用 grok 的 `image_edit` 合成開場畫面，再讓她開口。
- **對口型的口播片段**：稿子切成 ≤ 15 秒一段，通過 **grok CLI** 的 `reference_to_video` 用 **Grok Imagine Video 1.5** 生成。grok CLI 沒有音訊驅動口型；想用自己的錄音對口型，要另接 Wan 3.0、OmniHuman 等服務。
- **先報額度，再生成**：每次生成前，Agent 先報「段數 · 秒數 · 預估佔 grok 每週額度多少」，你點頭才開始；先拍第 1 段給你看，滿意再批次。
- **兩道質檢**：每段用 whisper 回聽、和稿子比對；每段抽 4 幀檢查（Grok 偶爾會自己往畫面裡燒字幕，有就重拍那段）。
- **聲音統一**：1/3 倍頻程頻譜匹配 + 去齒音 + 同一個小房間混響 + 響度統一，30 段分開生成的口播聽起來像一次錄完（實測齒音段間差 13.2 dB → 5.9 dB）。
- **按內容推薦剪輯風格**：Agent 先診斷內容，推薦 2 種風格並附預覽圖，一次問完（風格 · 比例時長 · 花字強度 · 主播）。
- **48 個包裝元件**：逐幀拆了 25 支頂尖創作者影片（MrBeast、Mark Rober、Ryan Trahan、MKBHD、影視颶風、何同學、Johnny Harris、Vox、Kurzgesagt、回形針、半佛仙人、差評、畢導）。每種風格自帶預設包裝，想加減直接說。
- **景深字**：大字 / 數字放在背景和人之間（macOS Vision 人像分割 → 透明影片 → 三層合成）。
- **多語言**：英、日、韓、法、西、阿拉伯語實測，whisper 回聽準確率 94–100%。
- **多種 Agent 都能用**：標準 `SKILL.md` Agent Skill + 腳本，只要能裝 Skill、能在本機跑命令（包括 grok CLI），就能驅動整條流程。

## 工作流程

```
你的內容 ──► 0. 環境檢查（grok CLI / ffmpeg / whisper，已經有的直接跳過）
              1. 診斷內容 → 5 種風格裡推薦 2 種 → 一次問完 → brief.json
              2. 寫稿 script.json（每段 ≤15 秒，中文約 5.4 字/秒）
              3. 報額度（佔 grok 每週額度）→ 等你確認 → 先拍第 1 段 → 你看過 → 批次
              4. grok CLI 逐段生成 → whisper 回聽 → 抽幀檢查
              5. 聲音統一（頻譜匹配 + 去齒音 + 同一房間混響）
              6. 逐字時間軸（tl.json）
              7. Remotion 剪輯：風格模板 + 預設包裝（+ 你點名的手法）
              8. 渲染 → 看過渡中間幀 → 響度（-14 / -16 LUFS）
```

<p align="center"><img src="docs/images/ad-breakdown.jpg" width="820" alt="直播間廣告 5 段，每段用的包裝"></p>

---

## 支援哪些 Agent

這個 Skill 是一個帶 `SKILL.md`（開放的 Agent Skills 格式）的資料夾，加上 Python / Shell / Remotion 腳本。要跑通**完整**流程，Agent 需要兩樣能力：

1. **能裝 Agent Skills**（技能目錄或上傳技能包）；
2. **能在你電腦上執行命令**（grok CLI 生成品段；ffmpeg、Python、Node 用來質檢、剪輯）。

| Agent | 裝 Skill | 本機執行命令 | 狀態 |
|---|---|---|---|
| **Claude Code** | `~/.claude/skills/` | ✅ | ✅ 已實測，這個倉庫就是用它做的；grok CLI 流程 2026-10-26 實測跑通 |
| **Codex**（CLI / 桌面） | `~/.codex/skills/` | ✅ | ✅ 預期可用（同一套腳本） |
| **OpenClaw** | 放進 OpenClaw 的技能目錄（見其文件） | ✅ | ⚙️ 應可用 |
| **WorkBuddy** | 技能 → 匯入資料夾 / 壓縮包 | ✅ 桌面端 Agent | ⚙️ 應可用，選單名以 App 當前版本為準 |
| **豆包** · **千問辦公** · **納米Work** 等 Agent 產品 | 產品支援 Agent Skills 就匯入 | 生成和剪輯都需要 | ⚙️ 滿足上面兩樣能力即可，具體入口以各產品文件為準 |
| **Claude 桌面端 / claude.ai** | 設定裡上傳技能包 | ⚠️ 只有沙盒 | 能寫稿、設計場景；生成和剪輯需要能在本機跑命令的 Agent |

> 如果你的 Agent 只能聊天、不能跑本機命令，可以先用它**寫稿、設計場景**；生成和剪輯交給 Claude Code / Codex，或者照 [`SKILL.md`](skills/digital-human-koubo/SKILL.md) 裡的命令手動跑。

---

## 安裝

### 1 · 下載程式碼

```bash
git clone https://github.com/yelban/digital-human-koubo.TW.git
cd digital-human-koubo.TW
```

### 2 · 把兩個 Skill 裝進你的 Agent

倉庫裡有兩個 Skill：`digital-human-koubo`（主 Skill）和 `finance-explainer`（風格 A「財經 / 科技解說」的引擎）。

**Claude Code**
```bash
mkdir -p ~/.claude/skills && cp -R skills/digital-human-koubo skills/finance-explainer ~/.claude/skills/
```
**Codex**
```bash
mkdir -p ~/.codex/skills && cp -R skills/digital-human-koubo skills/finance-explainer ~/.codex/skills/
```
**WorkBuddy / OpenClaw / 其他 Agent**：把兩個資料夾打成壓縮包，在產品的「技能」頁面匯入，或者複製進它的技能目錄（以產品文件為準）：
```bash
cd skills && zip -r ../digital-human-skills.zip digital-human-koubo finance-explainer && cd ..
```

### 3 · 安裝 grok CLI（AI 影片生成）

口播片段由 grok CLI 的 `reference_to_video` 工具生成（Grok Imagine Video 1.5），用的是你 grok 帳號的每週額度。實測 X Premium+ 帳號可用，其他方案沒測過。

| 系統 | 命令 |
|---|---|
| macOS / Linux / WSL | `curl -fsSL https://x.ai/cli/install.sh \| bash` |
| Windows（PowerShell） | `irm https://x.ai/cli/install.ps1 \| iex` |

裝完執行 `grok login`，在瀏覽器登入。生成前在 grok 裡確認兩項：

- `/privacy` 要是 **Opt in**（ZDR 零資料保留關著）。ZDR 開著時影片工具會直接拒絕。關著期間 grok 會把對話紀錄上傳 xAI，做完改回 **Opt out**。這個設定由你自己改，Agent 不會替你改。
- `/usage` 看本週額度還剩多少。

> xAI 文件寫可以配 S3 儲存桶（`tools.zdr_video_output_s3`）讓 ZDR 開著也能生成，但 2026-10-26 用個人帳號（grok 1.0.70）實測，放在哪個位置都不生效。

### 4 · 本機工具（質檢、剪輯要用）

| 工具 | macOS | Windows | Linux |
|---|---|---|---|
| ffmpeg | `brew install ffmpeg` | `winget install Gyan.FFmpeg` | `sudo apt install ffmpeg` |
| Python 3 + numpy + Pillow | `brew install python` 後 `python3 -m pip install numpy pillow` | `winget install Python.Python.3.12` | `sudo apt install python3-pip` |
| Node.js 18+（Remotion） | `brew install node` | `winget install OpenJS.NodeJS.LTS` | `nvm install --lts` |
| whisper.cpp（`whisper-cli`） | `brew install whisper-cpp` | [Releases 下載](https://github.com/ggerganov/whisper.cpp/releases) | [原始碼編譯](https://github.com/ggerganov/whisper.cpp) |
| whisper 模型 | 下載 [`ggml-medium-q5_0.bin`](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium-q5_0.bin) 放到 `~/models/`（或 `export WHISPER_MODEL=模型路徑`） | 同左 | 同左 |
| OpenCC（可選，稿子寫繁體時回聽比對用） | `brew install opencc` | [OpenCC](https://github.com/BYVoid/OpenCC) | `sudo apt install opencc` |

一條命令檢查（也會查 grok CLI 裝了沒、登入了沒）：已經裝好的打勾跳過，缺什麼列出多種裝法：
```bash
bash ~/.claude/skills/digital-human-koubo/scripts/doctor.sh
```

**景深字**（文字在人身後）用的是 Apple Vision，需要 **macOS**；其餘功能跨平台。

### 5 · 音效與佔位配樂

倉庫**不帶任何第三方音訊**。用程式碼合成一套原創音效（30 個）和一條佔位配樂（無版權）：
```bash
python3 ~/.claude/skills/digital-human-koubo/scripts/make_assets.py
```
`new_edit.sh` 每次起新工程也會自動跑。想要更好的配樂，把你有授權的曲子放到 `<工程>/public/music/bgm.mp3` 覆蓋即可。

### 6 ·（可選）小米 MiMo 語音：音色設計 / 聲音克隆

預設用 Grok 自帶的聲音（口型最準）。想要設計一個新音色、用你自己的克隆聲音，或者做純旁白影片，Skill 會呼叫 **小米 MiMo TTS**：

1. 去 **[platform.xiaomimimo.com](https://platform.xiaomimimo.com/)** 註冊並建立 API Key。寫這份文件時小米的 TTS 模型是限時免費的，具體以官網當前價格為準。
2. 把 Key 放進環境變數，或寫到 `~/.config/ai-teardown/mimo.env`：
   ```bash
   mkdir -p ~/.config/ai-teardown && cat > ~/.config/ai-teardown/mimo.env <<'EOF'
   MIMO_API_KEY=你的key
   MIMO_BASE_URL=https://api.xiaomimimo.com/v1
   EOF
   chmod 600 ~/.config/ai-teardown/mimo.env
   ```
3. 只克隆**你本人**的聲音，或明確授權給你的聲音。

> 注意：Grok 的口型跟的是它自己生成的聲音。事後換成別的聲音，口型會差約 100 毫秒（畫中畫看不出，全螢幕特寫看得出）。想用自己的錄音又要口型準，換「音訊驅動口型」的模型，比如 OmniHuman（這個 Skill 目前沒接）。

---

## 快速開始

直接用大白話跟 Agent 說：

```text
用我的數位人 Skill 講這段：……（貼上你的內容）
用這個數位人做一條 30 秒直播間廣告：WorkBuddy 上手課，10 節課 99 元，原價 999。
做一條 3 分鐘的小林式解說：矽谷銀行為什麼會暴雷。
講到這幾個國家的時候加地圖航線 / 把「¥99」放在她身後 / 開場加個預告閃回。
把包裝元件圖鑑發我看看
```

接下來會發生：
1. 環境檢查：已經裝好的直接跳過。
2. 一行診斷 + 推薦 2 種風格（附預覽圖），一次問完。
3. 稿子 + 場景設計 + **額度報價** → 你確認 → 先拍第 1 段 → 你確認 → 批次。
4. 質檢、修音，按風格預設包裝剪輯 → 出成品 MP4。

---

## 做你自己的數位人

1. 選一張照片：正臉、光線均勻、頭髮不擋臉、嘴閉著。**只用你本人或明確授權的照片。**
2. 存進 `skills/digital-human-koubo/assets/`（例如 `assets/my_host.jpg`），不用上傳。
3. 可選：讓 Agent 用 grok 的 `image_edit` 生成四視圖（正面、兩個側面、背面），保證換角度不變臉。
4. 把路徑寫進 `skills/digital-human-koubo/persona.json`（`grok.reference_image`；第二位主播寫在 `other_hosts.me.reference_image`）。
5. 先生成 1 段 8 秒左右的片段，看臉、口型、聲音滿意了再批次。

詳細步驟見 [`references/new-avatar.md`](skills/digital-human-koubo/references/new-avatar.md)。倉庫裡沒有作者本人的照片（`host_me_polo.jpg`），用第二位主播前請放入你自己的。

<p align="center"><img src="docs/images/scene-composite.jpg" width="720" alt="參考照 → 合成直播間"></p>

---

## 五種剪輯風格

<p align="center"><img src="docs/images/five-styles.jpg" width="820" alt="五種剪輯風格"></p>

| 風格 | 比例 | 時長 | 適合 | 模板 |
|---|---|---|---|---|
| **A** 小林式解說（財經 / 科技事件） | 16:9 | 3–20 分鐘 | 事件、資料、「為什麼」 | `finance-explainer` 引擎 |
| **B** 網紅花字口播 | 9:16 | 30–120 秒 | 安利、帶貨、種草、吐槽 | `templates/huazi-916`（資料驅動） |
| **C** 發布解讀 | 16:9 | 30–90 秒 | 新品、新模型發布 | `templates/reference/launch-169` |
| **D** 保姆級教學 | 16:9 | 3–8 分鐘 | 幾步做出 XX、工具上手 | `templates/reference/tutorial-169` |
| **E** 多主播 · 多語言 · 多場景 | 16:9 | 3–7 分鐘 | 能力展示、出海 | `templates/reference/multihost-169` |

風格 B 有三檔花字強度：**克制 / 標準 / 熱鬧**。

<p align="center"><img src="docs/images/huazi-presets.jpg" width="820" alt="三檔花字強度"></p>

風格 A 只學解說頻道的**結構和剪輯語法**，不用真實創作者的臉、聲音、佈景和原話。

---

## 48 個包裝元件

逐幀拆了 25 支影片（鏡頭切分、開場逐拍、螢幕文字、聲音），完整報告在 [`references/research/`](skills/digital-human-koubo/references/research/)。

<p align="center"><img src="docs/images/creator-pacing.jpg" width="720" alt="25 支頂尖創作者影片每分鐘切數"></p>

**從研究裡提煉的規則**（[`packaging-playbook.md`](skills/digital-human-koubo/references/packaging-playbook.md)）：
- 切數可以低，刺激不能斷：前 30 秒每 3–5 秒要有一個新東西出現。
- 前 3 秒直接給命題或動作，不問好、不放 Logo。
- BGM 從頭鋪到尾；音效只給事件（中文口播頭部每分鐘 1–3 個）；揭曉前刻意靜音 0.6–1.0 秒。
- 單機位數位人最便宜的節奏來源：按句子邊界跳切推近（1.0× / 1.18× / 1.32×）。

<p align="center"><img src="docs/images/packaging-gallery.jpg" width="820" alt="包裝元件圖鑑"></p>

| 分組 | 元件 |
|---|---|
| 開場 / 鉤子 | TeaserColdOpen 預告閃回 · ColdOpenFreeze 定格片名卡 · SearchTyping 搜尋框打字 · NumberSpike 數字釘子 · SlamText 砸字 · WordStack 逐詞堆疊 · TornStrip 撕紙標題 · **TextBehind 景深字** |
| 證據 / 資料 | EvidenceCard 證據截圖 · DocFocus 文件聚焦 · SourceDoc 官方文件 · ZoomFocus 截圖聚焦 · Counter 數字滾動 · Odometer 里程錶 · GlassPanel 玻璃面板 · SpecCard 參數卡 · LineDraw 折線圖 · BarCompare 對比條 · ReviewCards 評論卡 · ArchiveCards 檔案卡 · MapRoute 地圖航線 · CompareWipe 前後對比 · PaperCollage 紙張拼貼 |
| 標註 / 人物 | HandDraw 手繪圈注 · CalloutPill 指標膠囊 · LeaderLabel 引線標註 · TypedNameTag 打字名牌 · LowerThird 人名條 · NamePlate 名牌語錄 · SourceTag 出處角標 · FreezeFrame 定格「等等！」 |
| 節奏 / 互動 | PunchInHost 跳切推近 · KeywordStack 關鍵詞三連 · RetentionCaption 留存大字幕 · TiltLine 傾斜金句 · Aside 括號旁白 · Danmaku 彈幕 · ReactionPop 反應貼紙 · MemeWindow 梗圖窗 · PollPop 投票 · GlitchInterstitial 故障插屏 · HostFloaters 懸浮窗 · ProgressChapters 進度條 · ProgressTracker 步驟追蹤 · ChapterCard 章節卡 · RecapBoard 復盤板 · Countdown 倒計時 · GhostWord 鬼影大字 |

每個元件都在 `pack` 列表裡按名字呼叫，時間寫成「段:詞」（如 `"3:積分"`），9:16 自動適配：

```json
"pack": [
  { "use": "NumberSpike", "at": "1:不到十塊錢", "until": "1:end", "text": "¥9.9/節", "label": "一節課" },
  { "use": "Danmaku", "items": [{ "t": "真的假的？", "at": "1:" }, { "t": "AI 還能幫我幹活？", "at": "1:教你", "hot": true }] },
  { "use": "TextBehind", "src": "main.mp4", "cutout": "main_cut_s4.webm", "cutoutFrom": 17.2, "at": "4:", "until": "4:end",
    "mode": "count", "lines": [{ "t": "¥99", "font": "en", "color": "#FFE14D", "size": 0.17 }], "count": { "from": 999, "to": 99, "prefix": "¥" } }
]
```
參數說明：[`references/packaging.md`](skills/digital-human-koubo/references/packaging.md)。渲染前先檢查：`python3 scripts/check_edit.py <工程>/src`。

### 景深字：文字在人身後

<p align="center"><img src="docs/images/text-behind-layers.jpg" width="760" alt="原影片 → Vision 遮罩 → 原影片 + 大字 + 人像"></p>

```bash
python3 scripts/cutout_video.py public/main.mp4 public/main_cut_s4.webm --from 17.2 --to 22.4   # 只摳用到的那幾秒
```
適合**中景、頭頂留白**的畫面。自拍特寫裡人佔了約 89% 的畫面，字會被擋住，腳本在超過 60% 時會提醒。把這類段落標成 `"shot": "depth"`，生成時就會出中景。

<p align="center"><img src="docs/images/closeup-vs-medium.jpg" width="560" alt="特寫 89% 擋字，中景 57% 露字"></p>

---

## 成本參考（真實跑過的數）

生成用的是你 grok 帳號的每週額度，不是積分。grok 裡的 `/usage` 只顯示整數百分比，所以下面是範圍。

| 2026-10-26 實測（X Premium+） | 結果 |
|---|---|
| 4 段共 36 秒 720p | 用掉每週額度 10–12% |
| 每秒 720p | 約 0.25–0.35% |
| 480p | 還沒實測 |

估算：上面 27 秒的直播間廣告（5 段 720p）約佔每週額度 7–9%，不含場景圖。每週額度和 grok 的其他用途共用。上面的示例片當時是用 Renoise 積分做的。

## 目錄結構

```
skills/
  digital-human-koubo/            主 Skill
    SKILL.md                      Agent 照著執行的流程
    persona.json                  主播形象、聲音描述、提示詞模板
    references/                   風格選單 · 包裝元件 · 手法庫 · 安裝 · 拆解報告
    scripts/                      build_tasks · grok_generate · assemble · align · check_edit · cutout_video
                                  voicefx/unify · doctor · new_edit · make_assets
    templates/
      huazi-916/                  9:16 資料驅動花字口播模板（edit.json）
      packaging/                  48 個元件 + 圖鑑工程
      reference/                  launch-169 · tutorial-169 · multihost-169
    assets/                       風格預覽圖 · 包裝圖鑑 · 數位人參考圖
  finance-explainer/              風格 A 引擎（episode.json 拍表、檢索工具）
docs/                             README 用的圖片、GIF 預覽、封面幀
```

## 踩過的坑（Skill 裡都處理了）

- Grok 橫式口播偶爾**自己燒字幕**，提示詞寫了也擋不住 → 抽幀檢查，重拍那段。
- whisper 會把中文數字寫成阿拉伯數字（九百九十九 → 999），而且只輸出簡體，準確率會掉，但其實沒念錯 → `assemble.py` 比對前兩邊都把中文數字轉成阿拉伯數字、繁轉簡（要裝 OpenCC）。grok 念繁體稿的效果還沒測過。
- grok 的 mp4 多帶一條封面圖影片流 → 腳本只讀第一條影片流（`v:0`），不然會讀到兩組寬高。
- ZDR 開著時 grok 影片工具不能用 → 生成前 `/privacy` 改成 Opt in，做完改回 Opt out。
- Grok 9:16 720p 是 **720×1280**，別拉成別的比例。
- expo 緩動到不了終點（99.9 四捨五入成 100）→ 計數動畫結束時強制落在精確值。
- 主播影片軌一定要靜音；兩條聲音差幾毫秒疊在一起會刺耳（梳狀濾波）。

## 使用紅線

- 只用你本人或**明確授權**的臉和聲音，不冒充任何真人或創作者。
- 每條片子標「內容由 AI 數位人演繹」，場景和動物片段標「AI 生成」。
- 不編數字、價格、優惠、評價；畫面上的示意資料要標「示意」。
- 不用網路梗圖、影視劇截圖、明星照片；梗圖類元件用你自己數位人生成的原創貼紙。
- grok 額度只在你確認報價之後才用。

## 許可與第三方

- 程式碼和文件：[MIT](LICENSE) © 2026 Berryxia（andyhuo520）。
- 渲染用的 **[Remotion](https://www.remotion.dev/)** 有自己的許可：個人和 3 人以內的公司免費，更大的公司需要購買[公司授權](https://www.remotion.pro/)。
- 動態表情：[Google Noto Emoji Animation](https://googlefonts.github.io/noto-emoji-animation/)（CC BY 4.0），影片裡請署名「Animated emoji: Google Noto」。
- 地圖：[world-atlas](https://github.com/topojson/world-atlas)（ISC，資料來自 Natural Earth，公有領域）、[d3-geo](https://github.com/d3/d3-geo)、[topojson-client](https://github.com/topojson/topojson-client)（ISC）。涉及中國邊界的正式發布內容，請按國內相關規範另行核對。
- 語音識別：[whisper.cpp](https://github.com/ggerganov/whisper.cpp)（MIT）。生成走 xAI 的 grok CLI（用你自己 grok 帳號的每週額度）；可選 TTS 用 [小米 MiMo](https://platform.xiaomimimo.com/)。
- WorkBuddy 示例裡的課程截圖來自作者自己的課程。示例影片是作者的作品，請不要當成自己的作品二次上傳。

詳見 [THIRD_PARTY.md](THIRD_PARTY.md)。

---

<div align="center">

作者 **Berryxia** · 用 Claude Code 做的 · 有幫助的話點個 ⭐，讓更多人看到。

</div>
