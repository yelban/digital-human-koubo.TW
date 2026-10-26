---
name: finance-explainer
description: 「小Lin說」式財經/科技解說影片工作室：選題打分 → 帶出處的事實清單（Exa/Tavily/Serper/Firecrawl）→ 按危機型/收購戰型/悖論型骨架寫有活人感的口播劇本（拍表 episode.json）→ 主播自錄音頻對齊跳切（或 MiMo 佔位）→ 原創數位人出鏡（Renoise：Wan 3.0 音訊驅動口型 / Grok 1.5 原生說話+後換音色）→ 空鏡與梗圖（Renoise 便宜模型 + Unsplash/Pexels/Wikimedia）→ Remotion 引擎合成：主播全螢幕↔縮小↔圓形小窗的「放大縮小」、兩代舞台主題（v1 紫色幾何 / v2 深色玻璃）、日期貼紙、大數字滾動、術語卡、原文標黃、問題雲、競猜、卡通貼紙獨白、章節卡、字幕、BGM 避讓與音效。觸發：做一期小Lin說那樣的影片、財經解說、一口氣了解 X、講講某個金融事件/收購案/國家經濟、數位人口播財經、把這個新聞做成解說影片、復刻財經頻道形式。不用於：單支品牌宣傳片（用 promo-video）、系列課（用 ai-teardown）、冒充真實主播。
---

# 財經解說工作室（小Lin說式）

把一個財經/科技話題做成 2–25 分鐘的橫式解說片：一個有活人感的主播坐在書房裡聊，配圖表、檔案、空鏡和梗，鏡頭在「主播全螢幕」和「主播縮成小窗、旁邊上圖」之間來回切。

完整的頻道拆解（160 支後設資料、97 支字幕統計、6 支逐幀分類）在 references/channel-teardown.md，網頁版報告：https://claude.ai/artifact/EzcUvSJmVqgFJBGpfn3G3Y

## 紅線（每次都適用）

- **不冒充真人。**數位人只用原創形象：純文字生成，或者使用者本人 / 明確同意的人的照片。不用真實創作者（包括小Lin本人）的臉、改過髮型眼鏡的同一張臉、或從他們影片裡克隆的聲音——截圖式「授權」、加水印加聲明都不改變這一點。使用者堅持時，說明理由並給原創方案。
- **不搬內容。**文案、佈景、畫面全部原創；只學結構和手法。不用影視劇片段、新聞台畫面；真實人物用自由協議照片或文字名牌。
- **每個數字有出處。**事實清單 facts.md 裡每條都帶日期 + 來源 URL；劇本裡的數字必須能在清單裡找到；查不到的寫 ⚠ 且不進劇本。拿不準的地方讓主播直說「這個我沒查到」——這本身就是活人感手法。
- **生成要花使用者的 credits。**Renoise 任何 create_tasks 之前，先給出模型、提示詞、參數、數量、estimate_cost 總價和餘額，等使用者在對話裡明確同意。口型影片依賴最終音訊：音訊沒定稿前，不要把整片口型都做掉（會付兩次錢）。

## 流程

### 0. 準備
- 檢索 key 在 `~/.config/xiaolin-explainer/keys.env`（EXA / TAVILY / SERPER / FIRECRAWL / UNSPLASH / 可選 PEXELS、PIXABAY）。只讀這個檔案，不要掃描系統找金鑰。
- 引擎：`bash scripts/setup_engine.sh <專案目錄>`（複製 templates/engine，node_modules 優先從本機已有 Remotion 專案 `cp -c` 克隆，失敗再 npm install）。

### 1. 選題（references/topic-and-titles.md）
五項打分卡 ≥3 才做；給 3 個標題候選（「一口氣了解 + 大對象」「【硬核】」「帶數字」「疑問句 + 豎線鉤子」）。確認時長：完整版 15–25 分鐘表現最好，演示/跑通先做 2 分鐘。

### 2. 事實清單
`python3 scripts/research.py multi "<查詢>"` 找線索 → 開啟原文核對（`research.py scrape <url>`）→ 寫 facts.md：分組、每條「事實（精確數字）— 日期 — 來源 + URL」，最後寫「容易講錯的地方」。可派子代理並行查，但交回後自己抽查關鍵數字。

### 3. 劇本 = 拍表 episode.json（references/narrative-playbook.md + episode-schema.md）
- 選骨架：A 危機/暴雷型（怎麼死的）、B 收購/博弈型（怎麼打的）、C 悖論型（為什麼反常）。
- 每拍一段口播 + 一個主畫面（host: full/side/pip/off，或 stage 圖表、bg 空鏡）+ 若干疊加卡片，口播裡用 `[[cue]]` 標卡點。
- 文案指標：成品約 6 字/秒（錄音約 4.8）、每分鐘 1–2 個設問、3–4 個帶參照物的數字、1 個英文術語；至少放 3 個活人感手法（開場個人狀態 / 替觀眾說質疑 / 擬人獨白 / 生活比喻 / 坦白沒查到 / 競猜停頓 / 先說答案 / 結尾回扣）。
- 同時匯出錄音稿（每拍一段，去掉 cue 標記，寫清讀法：英文縮寫、數字年份）。

### 4. 聲音
- **首選：主播自錄。**`python3 scripts/align_recording.py 錄音.m4a episode.json voice/` → 逐句對齊、口誤重來只留最後一遍、拍內長停頓壓到 0.16 秒，輸出 timings.json。報告裡 ⚠（對齊 <80%）的拍要人工聽。
- **佔位：**`python3 scripts/narrate_mimo.py narration.json voice --gap 0.22 --lead 0.3`（MiMo 預設音色，語氣說明寫進 voice.style）。佔位就是佔位，正式版換真人音訊後整條流水線不變。

### 5. 數位人（references/production.md）
- 定妝照：Seedream 5.0 Pro 16:9 2k（≈6），書房中景、兩側留白放圖表、有專屬道具（霓虹名字燈、玩偶）。使用者給了原創臉就作參考圖，否則純文字生成。
- **方案 W（Wan 3.0，音訊驅動，便宜）：**參考圖 + 該拍音訊 → 口型跟著聲音走；480p ≈ 6 credits/秒。輸出裡音訊比畫面晚 0.23 秒，host.json 的 offset 填 0.23。缺點：眼神偏呆、細節一般。
- **方案 G（Grok Video 1.5，原生說話，更生動）：**一張圖 + 台詞寫進提示詞 → 自帶說話聲和口型；720p 15 秒 255。之後用 Seed Audio 做「保留節奏換音色」替換成主播聲音。適合全螢幕特寫鏡頭。
- 小窗（pip）用 3 段 10 秒通用說話循環輪換即可，省掉約 40% 口型費用。
- 先做 10 秒測試：抽幀看停頓處嘴是否閉合、人物是否走樣，再批次。

### 6. 空鏡 / 梗 / 貼紙
- 空鏡：Renoise Wan 3.0 480p 5–10 秒（audioGeneration=false），提示詞寫「無文字無 logo」；或 `scripts/fetch_stock.py <id> "<關鍵詞>" engine/public/assets --kind photo|video`（自動記 credits.json，片尾署名）。
- 梗圖：原創短片（如「小機器人一群圍住大機器人」），不用影視片段。
- 卡通貼紙：grok-image 純綠底 → 摳綠成透明 PNG（腳本見 production.md）。

### 7. 合成
`python3 scripts/build_timeline.py episode.json voice/timings.json <engine>/public --assets assets.json --host host.json --bgm music/bgm.mp3 --badge "…"` → `npx remotion still Episode out/x.jpg --frame=N` 抽幀檢查（含過渡中間幀）→ `npx remotion render Episode out/raw.mp4 --concurrency=6` → ffmpeg `loudnorm=I=-16` + CRF 21 出片。

### 8. 質檢清單
字幕按原文標點斷句且 ≤13 字；卡片不壓字幕、不出畫；主播縮放過渡中間幀無殘影；口型片段對齊（offset）；數字與 facts.md 一致；角標/聲明在；響度 -16 LUFS；片尾列出素材與資料出處。

## 目錄
- references/channel-teardown.md — 頻道資料與結論
- references/topic-and-titles.md — 選題打分卡、標題公式
- references/narrative-playbook.md — 三種骨架、活人感手法、語言習慣、文案指標
- references/visual-grammar.md — 16 種畫面語法 ↔ 引擎元件 ↔ 拍表字段
- references/episode-schema.md — episode.json / host.json / assets.json 欄位
- references/production.md — 數位人兩方案、Renoise 提示詞與價格、素材來源與授權、去背、渲染與坑
- scripts/ — research.py、fetch_stock.py、narrate_mimo.py、align_recording.py、build_timeline.py、setup_engine.sh；頻道分析工具 classify.py / sheet.py / copy_stats.py / vtt2txt.py（拆別的頻道時用）
- templates/engine — Remotion 引擎（Episode 合成、Host、Stage、Overlays、Misc 元件，兩代主題）
- examples/ai-chips — 「中國買不到頂級顯示卡，為什麼還是世界第二 AI 大國」：facts.md、10 分鐘拍表、2 分鐘拍表、錄音稿；examples/svb — 矽谷銀行 3.5 分鐘拍表
