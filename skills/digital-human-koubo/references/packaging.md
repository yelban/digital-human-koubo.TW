# 包裝元件庫（48 個，templates/packaging/kit）

所有剪輯模板都能用。**寫法統一**：一個 `pack` 陣列，每條 `{ "use": "元件名", ...參數 }`。
- 時間欄位 `at` / `until`（包括數組裡巢狀的，如 `words[].at`、`pins[].at`）可以寫 `"段:詞"`（如 `"3:積分"`、`"3:"` 段首、`"3:end"` 段尾、`"3:詞#2"` 第 2 次出現），也可以寫秒數。
- 有頂層 `at` 的元件只在 `[at, until]` 裡出現；沒寫 `until` 就是 `at + dur + 3.5` 秒（`hold` 可改）。
- 9:16 直式時，沒寫位置參數的元件自動用直式預設位置。
- **全螢幕類**會蓋住主播（口播聲音照常）——這正是「用 B-roll 蓋住口型難的段」的做法；**疊加類**疊在主播上。

在 9:16 花字模板裡寫進 `src/edit.json` 的 `"pack"`；在 16:9 參考工程裡 `import { PackLayer } from "./kit/registry"`，`<PackLayer items={pack} T={時間解析} />`。

**看效果**：`assets/packaging/图鉴.jpg`（每個元件一格），完整演示片 `templates/packaging` 裡 `npx remotion render src/index.ts Gallery`（成品：倉庫 Releases 裡的 packaging-gallery.mp4）。使用者問「有哪些包裝」時先發圖鑑。

## 開場 / 鉤子
| 元件 | 類型 | 做什麼 | 關鍵參數 | 來源流派 |
|---|---|---|---|---|
| TeaserColdOpen | 全螢幕 | 後面最炸的 3–5 個瞬間各閃 0.4–0.8 秒 + 「接下來」角標 → 問題字卡 | clips[{src,offset,dur,label,img}], question | 英文頂流 |
| ColdOpenFreeze | 全螢幕 | 動作片段 → 定格去色 → 「未完待續」箭頭 → 片名卡 → 雪花轉場 | src, freezeAt, until, title[2], vol | 半佛 |
| SearchTyping | 全螢幕 | 中性搜尋框逐字打 + 聯想詞 + 推近 1.6× | query, suggestions[], cps | Johnny Harris |
| NumberSpike | 疊加 | 大數字從 3 倍大 0.5 秒縮到頂部 + 同色閃光，可再縮成角標常駐 | text, color, label, pinAt | MrBeast |
| SlamText | 疊加 | 兩行大字先後砸進畫面上下，可帶年份角標 | lines[], stagger, year | Johnny Harris / Kurzgesagt |
| WordStack | 全螢幕 | 逐詞堆疊，一拍一個詞，最後一詞換色放大 | words[{t,at}], until | Mark Rober |
| TornStrip | 疊加 | 撕紙標題條橫穿畫面（片名 / 章節） | title, sub | 回形針 |
| **TextBehind** | 全螢幕（含主播） | **景深字：大字 / 數字在人身後**（原影片 → 大字 → 摳出來的人），升起 / 砸入 / 數字滾動 / 滑入 | src, cutout, lines[{t,color,size,font,outline}], mode, y, count{to,unit}, gradient, bgDim, crop, zoom, cutoutFrom | 影視颶風 / MrBeast / 差評 |

## 證據 / 資料
| 元件 | 類型 | 做什麼 | 關鍵參數 | 來源 |
|---|---|---|---|---|
| EvidenceCard | 全螢幕 | 截圖飛入 + 品牌色描邊 + 滑鼠指標 + 推近數值籤 + 3D 傾斜 | src, iw, ih, focus{x,y}, label, labelAt, tilt, source | 差評 |
| DocFocus | 全螢幕 | 重建文件，非目標句壓暗 35%，關鍵詞黃塊掃過 | title, source, paras[[{t,focus,hl,hlAt}]] | Vox / JH |
| SourceDoc | 全螢幕 | 官方文件截圖慢推 + 中文譯句熒光底 + 來源角標 | src, iw, ih, zh, source | 影視颶風 / 何同學 |
| ZoomFocus | 全螢幕/框 | 截圖 / 螢幕錄影推近到目標框 + 壓暗 + 標籤（不越過原圖邊緣） | src, iw, ih, focus{x,y,w,h}, label, zoom, box | 教學通用 |
| Counter | 疊加 | 數字滾動，落地彈一下 | to, from, unit, prefix, label, dur | 通用 |
| Odometer | 疊加 | 里程錶逐位滾動，高位先停 | value(字串), unit, label | 質感派 |
| GlassPanel | 疊加 | 毛玻璃資料面板，條形和數字一起滾 | title, unit, rows[{label,value,highlight}], note | 質感派 |
| SpecCard | 疊加 | 質感參數卡：大數字小單位、留白、逐行淡入 | rows[{k,v,u}] | MKBHD |
| LineDraw | 全螢幕 | 多條折線畫出，末端掛同色標籤 | series[{label,color,data}], xLabels, source | JH / Vox |
| BarCompare | 全螢幕 | 橫條對比 + 鬼影大字背景 | rows[{label,value,text,color}], ghost | 回形針 |
| ReviewCards | 疊加 | 評論 / 差評卡每 1.1 秒連彈（示意評論要標註） | cards[{name,stars,text,avatar}], per | Ryan Trahan |
| ArchiveCards | 全螢幕 | 檔案卡 0.6 秒一張快切 + 紅色標籤 | images[{src,label}], per | Johnny Harris |
| MapRoute | 全螢幕 | 世界地圖推近 + 國家高亮 + 圖釘 + 航線生長 | camera[{at,lon,lat,zoom}], highlight[{name,at}], pins[], routes[], theme | Johnny Harris |
| CompareWipe | 全螢幕/框 | 前後對比擦除 | a, b, la, lb, split | 通用 |
| PaperCollage | 全螢幕 | 紙紋底 + 白邊照片 + 膠帶 + 手寫批註 | items[{src,x,y,w,caption}], title, note | Vox / 回形針 |

## 標註 / 人物
| 元件 | 類型 | 做什麼 | 關鍵參數 |
|---|---|---|---|
| HandDraw | 疊加 | 手繪圈 / 箭頭 / 下劃線 / 打叉，描邊生長 | kind, x, y, w, h, from, color |
| CalloutPill | 疊加 | 實色膠囊 + 小尖指向目標，彈簧彈出 | text, sub, x, y, color, pointer |
| LeaderLabel | 疊加 | 引線 + 中文粗體 + 英文小斜體（+ 牛皮紙小標籤） | target[x,y], zh, en, dir, len, tag |
| TypedNameTag | 疊加 | 手繪箭頭指人 + 粗襯線名字逐字打出 + 頭銜 | name, title, x, y, target |
| LowerThird | 疊加 | 色條 + 名字 + 身份兩層滑出 | name, title, color, x, y |
| NamePlate | 疊加 | 去色人物旁雙層名牌 + 語錄藥丸氣泡 | name, title, quotes[{t,at}], x, y, qx, qy |
| SourceTag | 疊加 | 出處角標（每個資料都掛） | text, side, y |
| FreezeFrame | 全螢幕 | 定格 + 去色 + 「等等！」+ 圈注（打斷節奏） | src, label, note, mark |

## 節奏 / 互動 / 結構
| 元件 | 類型 | 做什麼 | 關鍵參數 |
|---|---|---|---|
| PunchInHost | 主播層 | 同一條口播按句子邊界硬切景別（1.0/1.3 或 1.0/1.18/1.32 + 偏置） | src, cuts[], scale, levels[{s,dx}], anchor |
| KeywordStack | 疊加 | 主播身旁依次彈 圖示 + 彩色詞，結束一起模糊淡出 | items[{t,at,icon,color}], until, x, y |
| RetentionCaption | 疊加 | 留存大字幕：1–3 個詞一組居中砸出，關鍵詞變色 | words[{t,at,key}], y, size, group |
| TiltLine | 疊加 | 傾斜 -12° 金句逐字彈出，關鍵詞亮黃 | text, keys[], tilt |
| Aside | 疊加 | 括號旁白吐槽（剪輯師畫外音） | items[{t,at,until,x,y}] |
| Danmaku | 疊加 | 彈幕從右往左飄（替觀眾說出質疑） | items[{t,at,hot}], lanes |
| ReactionPop | 疊加 | 動態表情 / 原創貼紙 + 吐槽，彈出輕晃 | emoji / img, caption, x, y |
| MemeWindow | 全螢幕 | 黑底梗圖窗，一句一圖硬切（素材用原創表情包） | items[{src,at,caption,pos}], until |
| PollPop | 疊加 | 「評論區打 1 還是 2」，說到哪個哪個大數字彈出 | question, options[{n,t,at}] |
| GlitchInterstitial | 全螢幕 | 0.5 秒測試卡故障插屏 + 圓形主播 + 「點贊關注」 | dur, text, host |
| HostFloaters | 疊加 | 主播旁漂兩個瀏覽器視窗 + 圖示小標籤 | windows[{src,pos,title}], chips[{t,icon,at,x,y}] |
| ProgressChapters | 疊加 | 頂部進度條 + 章節刻度 + 當前章節名 | chapters[{at,t}], total |
| ProgressTracker | 疊加 | 步驟徽章 / 路線條（起點 → 終點） | mode, steps[], stepAt[], from, to, progress[{at,v}] |
| ChapterCard | 全螢幕 | 色條掃過 + 大序號 + 標題 | n, title, sub, color, solid |
| RecapBoard | 全螢幕 | 兩欄復盤板（為什麼 / 怎麼辦），每章亮一條新的 | columns[{title,color,items}], reveal[] |
| Countdown | 疊加 | 倒計時藥丸，最後 3 秒變紅跳動 | seconds, label |
| GhostWord | 疊加 | 背景巨大鬼影詞緩慢橫移 | text, outline, opacity |

## 景深字 TextBehind 怎麼做
1. 先去背（macOS Vision 人像分割，只摳要用的那幾秒）：
   `python3 scripts/cutout_video.py public/main.mp4 public/main_cut_s3.webm --from 16.0 --to 19.5`
   出透明 webm + 一條灰度遮罩（檢查用）。邊緣有背景灰邊就加 `--shrink 2`；頭髮絲被吃掉就 `--shrink 0 --grow 1`。
2. pack 裡寫：`{ "use": "TextBehind", "src": "main.mp4", "cutout": "main_cut_s3.webm", "cutoutFrom": 16.0, "at": "3:體驗最好", "until": "3:end", "lines": [{ "t": "體驗最好" }], "gradient": ["#FFFFFF", "#C9D2E0"] }`
   數字：`"mode": "count", "lines": [{ "t": "23", "font": "en", "color": "#FFE14D", "size": 0.42 }], "count": { "to": 23 }`
3. 字放在頭肩後面（y 預設 0.36，直式 0.28），字越大越好（橫式 0.3–0.45 畫面高）；人像背景越乾淨效果越好。主播在模板裡有推近時把 `zoom` 設成同樣倍數，避免進出時取景跳一下。
4. **素材要求：中景、頭頂和兩側有背景。** 實測橫式中景（人佔畫面約 28%）效果很好；直式自拍特寫（人佔 89%）字幾乎全被擋住——去背腳本會在人像佔比超過 60% 時提醒。要用景深字的那幾段，生成口播時提示詞加「medium shot, leave headroom and background on both sides」。
5. 適合：開場命題、關鍵數字、章節名、金句。一支片 2–4 次，別每句都用。

## 例子（9:16 花字口播的 edit.json）
```json
"pack": [
  { "use": "NumberSpike", "at": "1:23 積分", "text": "23 積分", "label": "做一個數位人形象", "pinAt": "1:end" },
  { "use": "Danmaku", "items": [{ "t": "真的假的", "at": "3:" }, { "t": "這麼方便？", "at": "3:不是專業", "hot": true }] },
  { "use": "ZoomFocus", "src": "media/screen.png", "iw": 2880, "ih": 1800, "at": "7:", "until": "7:end", "focus": { "x": 2520, "y": 30, "w": 330, "h": 70 }, "label": "右上角註冊" },
  { "use": "PollPop", "at": "9:", "until": "9:end", "question": "你會用數位人起號嗎？", "options": [{ "n": "1", "t": "會", "at": "9:起號" }, { "n": "2", "t": "再看看", "at": "9:end" }] },
  { "use": "GlitchInterstitial", "at": "10:", "dur": 0.5, "text": "點贊關注" }
]
```
寫完跑 `python3 scripts/check_edit.py <工程>/src`（會檢查 pack 裡所有時間引用）。

## 素材
- 動態表情：`public/emoji/`（Noto，59 個；缺的用 promo-video 的 fetch_noto_emoji.py 補）。片尾加「Animated emoji: Google Noto」。
- 地圖：world-atlas（Natural Earth 110m，公有領域）。涉及中國邊界的正式發布內容，按國內規範另行核對。
- 梗圖 / 反應貼紙：用數位人定妝圖生成 20 種表情貼紙，或原創 IP 動物，不用網路梗圖。
