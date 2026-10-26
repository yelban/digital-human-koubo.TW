# 網紅花字口播模板（templates/huazi-916）

9:16，1080×1920，30fps。**內容全在 `src/edit.json`，時間全來自 `src/tl.json`**——改稿只動這兩個檔案。

## 起一個新工程
```bash
bash ~/.claude/skills/digital-human-koubo/scripts/new_edit.sh huazi-916 <工程目錄>
```
然後放素材：`public/main.mp4`（拼好的數位人口播，直式）、`public/voice.wav`（處理過的人聲）、`public/show/`（要展示的作品）、`src/tl.json`（`scripts/align.py` 的輸出）。

## edit.json 欄位
時間寫法：`"3:"` 第 3 段開頭 · `"3:end"` 第 3 段結束 · `"3:關鍵詞"` 這個詞開始 · `"3:關鍵詞#2"` 第 2 次出現 · 數字 = 絕對秒。

| 欄位 | 作用 | 例子 |
|---|---|---|
| `preset` | 花字強度 克制 / 標準 / 熱鬧 | `"標準"` |
| `title` | 頂部膠囊標題 | `{"left":"真實體驗","right":"我為什麼推薦 Renoise"}` |
| `chapters` | 章節膠囊（自動編 ①②③） | `[{"at":"4:","t":"隱私：MCP vs CLI"}]` |
| `keys` | 字幕裡變色放大的關鍵詞 | `["太臃腫","強烈建議"]` |
| `emojis` | 臉兩側彈的動態表情 | `[{"at":"2:太臃腫","e":"😵‍💫","side":"r"}]` |
| `punch` | 鏡頭推一下的時刻（不寫就每段第一個關鍵詞） | `["1:最大"]` |
| `cards` | 卡片，見下表 | |
| `showcase` | 主播縮小窗、全螢幕放作品 | `[{"from":"8:尤其","to":"8:end","items":[{"src":"show/a.mp4","label":"復刻"}]}]` |
| `cta` | 結尾號召大字 | `{"at":"11:強烈建議","text":"強烈建議","sub":"去試試 Renoise","subAt":"11:去試試"}` |
| `music` | 配樂 | `{"src":"music/bgm.mp3","vol":0.075}` |
| `badge` / `credits` | 左上角 AI 標識 / 片尾署名 | 預設「內容由 AI 數位人演繹」 |
| `brand` | 主色 | `"orange"` / `"#FF7A1A"` |

### 卡片類型（cards[].type）
每張卡片都有 `at`，可選 `until`（預設到本段結束、下一張卡片或 4.5 秒，取最早）。

| type | 長什麼樣 | 什麼時候用 | 關鍵欄位 |
|---|---|---|---|
| `stamp` | 斜蓋的描邊印章 | 結論、「不用抽卡」 | text, color, x, y, rot |
| `slam` | 描邊大字砸屏 | 吐槽、情緒最高點 | text, color |
| `big` | 黃色漸變大字塊 | 標籤式結論「起號神器」 | text |
| `number` | 數字滾動 | 價格、數量、積分 | value, unit, prefix, label |
| `vs` | 左右名牌 + VS | 對比兩家 | left{at,t}, right{at,t} |
| `tags` | 2×2 彩色名牌逐個點亮 | 支援的平台 / 工具 | title, items[{at,t,color}] |
| `bars` | 橫條對比 | 速度 / 價格對比（標「個人體驗」） | title, items[{t,v,label,color}], note |
| `list` | ✅ / ❌ 清單 | 優缺點、兩面 | title, items[{t,tone,at}] |
| `image` | 帶白邊的截圖 | 官網、介面、聊天記錄 | src, label, x, y, w, rot |

顏色可寫 yellow / pink / cyan / red / green / orange / purple / white 或十六進位制。

## 三檔花字強度（對比圖：assets/styles/B_huazi_presets.jpg，選強度時發給使用者）
| | 克制 | 標準 | 熱鬧 |
|---|---|---|---|
| 字幕字號（普通 / 關鍵詞） | 66 / 76 | 76 / 92 | 82 / 106 |
| 關鍵詞顏色 | 黃 | 黃 | 黃 / 粉 / 青 輪換 |
| 逐字彈跳 | 很輕 | 明顯 | 更彈 |
| 表情 | 隔一個出一個，偏小 | 全部 | 全部，更大 |
| 跳切推近 / 重點推鏡 | 不交替 / 很輕 | 1.09 / 14% | 1.11 / 20% |
| 段間閃白 | 無 | 有 | 更亮 |
| 音效 | 0.6 倍 | 正常 | 1.2 倍 + 推鏡處加 pop |
適合：克制 = 知識、品牌、嚴肅話題；標準 = 大多數口播；熱鬧 = 帶貨、搞笑、年輕向。不管哪檔都**不做整段抖動**，只在關鍵幀推鏡。

## 寫 edit.json 的習慣（參考爆款口播）
- 關鍵詞：每段 1–3 個，挑「情緒詞 + 數字 + 產品名」，不要整句都標黃。
- 表情：每分鐘 6–10 個，跟情緒走（驚訝 😱、推薦 😍、吐槽 😤、秘密 🤫、成功 💯），左右交替。
- 卡片：一段最多一張；一屏只說一件事，內容完整放下，別拆碎。
- 引用別人的說法（評測、扒料）在卡片 title 裡寫「網友分析 / 個人體驗」。
- 作品展示 ≥ 3 秒一個，最多 3 個。

## 檢查 + 渲染
```bash
python3 ~/.claude/skills/digital-human-koubo/scripts/check_edit.py <工程>/src     # 所有時間引用能對上才往下
npx remotion still src/index.ts Huazi out/a.jpg --frame=<幀>                    # 抽卡片、表情、展示過渡的中間幀
npx remotion render src/index.ts Huazi out/raw.mp4 --concurrency=6
ffmpeg -i out/raw.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v libx264 -crf 20 成品.mp4
```
示例資料：模板自帶的 tl.json / edit.json 是「Renoise 推薦口播」那期（11 段 · 88 秒），可以直接照著改。
