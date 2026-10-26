# 畫面語法圖鑑 ↔ 引擎元件 ↔ 拍表字段

原頻道兩代形式：
- **v1（2022–23）**：客廳佈景 + 名字霓虹燈；圖表上「紫色幾何舞台」，主播整幀縮成左下角矩形小窗。
- **v2（2025–）**：白書架；深色玻璃風氣泡/卡片舞台，主播縮成圓形頭像；新增 AI 卡通人物貼紙演戲、主播去背疊素材牆。

引擎主題：`meta.theme = "v1-purple" | "v2-glass"`（templates/engine/src/lib/theme.ts）。復刻用自己的佈景（示例：胡桃木書架 + 綠檯燈），只沿用語法。

| # | 畫面語法 | 什麼時候用 | 拍表寫法 | 元件 |
|---|---|---|---|---|
| 1 | 主播中景 | 觀點、情緒、過渡句 | `"host": "full"` | Host |
| 2 | 推近蓋跳切 | 全螢幕拍之間、關鍵句 | `"punch": 1.08–1.15` | Host（繞臉硬切放大） |
| 3 | 縮小 + 卡片（私信卡） | 開場觀眾點題 | `"host": "shrink"` + `comment` | Host + Comment |
| 4 | 側移 + 右側卡 | 術語、清單、貼紙獨白 | `"host": "side"` + `term`/`list`/`sticker` | Host |
| 5 | 小窗 + 圖表舞台（放大縮小） | 資料、檔案、步驟、競猜 | `"host": "pip"` + `stage` | Host + StageLayer |
| 6 | 全螢幕空鏡 | 提到具體事物、主播無需出鏡 | `"host": "off", "bg": "gen:xxx"` | Asset（Ken Burns 慢推） |
| 7 | 章節標題卡 | 每章開頭、片尾 | `{"kind":"chapter","title","subtitle","bg","duration":2.6}` | Chapter + impact 音效 |
| 8 | 日期貼紙疊加 | 時間線，倒下的劃紅線 | overlay `datestack`（items 帶 at、strike） | DateStack |
| 9 | 大數字滾動 | 金額、數量衝擊 | overlay `counter`（money:true 寫滿零） | Counter + ding |
| 10 | 蓋章 / 大字 / 毛筆字 | 吐槽、結論、一詞收尾 | overlay `kinetic` style big / stamp / stamp-red / brush | Kinetic + slam |
| 11 | 術語卡 | 英文術語 + 中文解釋 | overlay `term`（en, zh） | Term |
| 12 | 問題雲 | 本期議程 | overlay `questions`（items） | Questions |
| 13 | 原文標黃 | 公告、財報、新聞一手證據 | `stage.type = "doc"`（lines: text + hl） | Doc（逐行熒光筆） |
| 14 | 柱狀 / 折線 / 步驟 | 資料對比、時間軸拉鋸、原因清單 | `stage.type = bars / line / steps`（每項 at） | Bars / Line / Steps + callout |
| 15 | 競猜 | 「你猜多少錢？」 | `stage.type = "quiz"`（ask, reveal, answer） | Quiz |
| 16 | 卡通貼紙獨白 | 擬人內心戲 | overlay `sticker`（src, bubble 逐句） | Sticker（浮動 + 氣泡） |
| 17 | 反應梗 | 情緒出口 | overlay `meme`（src, caption） | Meme（全螢幕） |
| 18 | 要點清單 | 好/壞兩面、兩件事 | overlay `list`（tone good/bad） | List |
| — | 字幕 | 全程 | 自動（按原文標點斷句 ≤13 字，英文不拆） | Subtitles |
| — | 角標 / 聲明 | 演示片 | `--badge "AI 生成數位人演示 · 非商用"` | Badge |

尚未實現（需要時再加）：主播去背疊素材牆（v2，需 Vision 人像分割）、人名條 + 黃色手寫外號、氣泡關係圖（v2 玻璃氣泡）、自拍插入。

## 節奏參數（來自 6 支樣片逐幀統計）
- 每分鐘約 9–12 次畫面類型切換；硬切間隔中位數約 3 秒。
- 2023 年版：真人全景約 50%，最長一口氣 68 秒；2026 年版：真人全景 13–17%，最長 ≤8 秒。拍表裡主播全螢幕一次別超過 12 秒，長段落拆成「全螢幕 → 小窗圖表 → 全螢幕」。
