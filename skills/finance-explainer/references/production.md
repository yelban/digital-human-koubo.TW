# 製作手冊：數位人、素材、合成

價格是 2026-10-21 實測（Renoise credits）。生成前一律 estimate_cost → 給使用者看模型、提示詞、數量、總價 → 等明確同意。

## 1. 主播形象（定妝照）

- Seedream 5.0 Pro，16:9，2k，≈6 credits。
- 構圖：書房中景、人物居中、頭在上三分之一、**兩側留白**（放卡片和圖表）；專屬道具：暖黃霓虹名字燈、玩偶、一盞標誌性檯燈。
- 佈景要和被參考的頻道明顯不同（原頻道 v1 是客廳霓虹、v2 是白書架；示例集用胡桃木書架 + 綠色檯燈）。
- 使用者提供原創臉 → 作 reference_image，提示詞寫「keep her face, hairstyle and outfit exactly the same」。
- **身份核查**：使用者給的臉如果被描述為某位真實創作者，或與前一張被描述為真人的照片五官、飾品一致只改了髮型眼鏡，不要用；純文字生成或換一張確實不同的原創臉。

## 2. 數位人兩方案（實測對比）

| | W：Wan 3.0 音訊驅動 | G：Grok Video 1.5 原生說話 |
|---|---|---|
| 輸入 | 定妝照 + 該拍音訊（reference_audio） | 定妝照（只能 1 張）+ 提示詞裡寫台詞 |
| 口型 | 跟著給定音訊走；停頓處偶爾不閉嘴 | 與它自己生成的聲音天然一致 |
| 表情眼神 | 偏呆，變化少 | 靈動：眨眼、挑眉、歪頭、手勢豐富 |
| 解析度 | 480p（720p 翻倍價） | 720p / 480p |
| 價格 | 480p 6/秒 | 720p 17/秒、480p 10/秒 |
| 時長 | 2–30 秒 | ≤15 秒/段 |
| 聲音 | 就是你的最終音訊 | Grok 的聲音，事後「換音色」 |
| 坑 | 輸出音訊比畫面晚 0.23 秒 → host.json offset 0.23 | 每段音色略有差異；型號要寫中文讀法（A一百、H二十）否則會念英文 |

**推薦組合**：全螢幕和側移鏡頭用 G（720p）；圓形小窗和被空鏡蓋住的拍用 G 480p（只取聲音）或 W；預算緊時小窗用 3 段 10 秒通用說話循環輪換。

### W 提示詞（中文效果好）
```
@task:<定妝照> 中的主播坐在沙發上正對鏡頭講話，口型與 @material:<該拍音訊> 的中文語音逐字同步；說話停頓時嘴巴自然閉合，表情親切自然、不誇張，偶爾點頭、眨眼，雙手做解釋性手勢；固定機位中景，不推拉，人物長相、髮型、服裝、場景和光線與參考圖完全一致。音訊：只用參考音訊的人聲。無字幕、無水印。
```
duration = ceil(該拍音訊秒數)；「俏皮、挑眉」之類會讓表情蓋過口型，少寫。

### G 提示詞（英文描述 + 中文台詞）
```
She looks straight into the camera and talks to the viewer in lively, natural Mandarin Chinese, like a friendly finance YouTuber chatting with a friend: bright attentive eyes that track the lens, natural blinks, an occasional raised eyebrow and quick smile on key words, small head tilts and nods, expressive explaining hand gestures. Fixed medium shot, no camera movement; her face, hair, outfit and the study stay exactly the same.
She says, in Mandarin: "<該拍台詞，型號寫中文讀法>"
Sound: only her clear speaking voice in a quiet room; no music, no other sounds. No subtitles, no watermark.
```
duration = min(15, ceil(字數/5.2)+1)。實測 Grok 語速約 5.2–5.6 字/秒，15 秒能說約 80 字。一段長片含多拍時，用 clips.json 的 from/to 切視窗複用。

### 接入
- W：`build_timeline.py … --host host.json`，host.json 裡 `clips: {拍id: "host/xx.mp4"}`、`offset: 0.23`；沒有專屬片段的拍用 `loops` 自動輪換。
- G：`python3 scripts/grok_beats.py episode.json clips.json voice --public <engine>/public --host-out host.json` → 逐拍對齊、只裁首尾靜音、畫面同步偏移 → 直接餵給 build_timeline。
- 換音色（G 方案收尾）：把 voice/narration（或逐拍 audio）交給保留節奏的換聲（Seed Audio 1.0 re-voicing 等），輸出按 timings 逐拍切回 audio/<id>.wav，重跑 build_timeline 即可；口型不受影響。
- 抽檢口型：截停頓處與說話處的臉部特寫對比（停頓應閉嘴）；腳本裡 mouth_seq 的做法：每 0.1 秒一幀 + 當時音量 dB。

## 3. 聲音

- **主播自錄（首選）**：`align_recording.py 錄音 episode.json voice/` — 逐段 whisper（整段長錄音 + 長提示會漏句編句，已改為按 ≥0.45 秒停頓切段逐段轉寫）、重錄取最後一遍、拍內停頓 >0.28 秒壓到 0.16 秒、接縫 4ms 淡入淡出。
- **佔位**：MiMo 預設音色（男：白樺/蘇打；女：茉莉/冰糖），`narrate_mimo.py`；英文縮寫寫進 lexicon 拆字母讀（GPU→G P U），型號寫中文讀法。
- **不做**：從真實創作者的影片裡擷取聲音做克隆參考。

## 4. 空鏡、梗、貼紙

- Wan 3.0 480p，audioGeneration=false，5 秒 30 / 10 秒 60。提示詞寫清「no readable text or logos」「slow dolly / slow orbit」。長拍用 10 秒片 + 引擎裡的 Ken Burns 慢推。
- 素材庫：`fetch_stock.py <id> "<英文關鍵詞>" <public>/assets --kind photo|video [--source unsplash|pexels|pixabay|wikimedia]`。Unsplash 自動打 download 端點並記署名；Wikimedia 只收 CC0 / CC BY / CC BY-SA / PD；credits.json 用於片尾致謝。
- 梗：原創 3D 卡通短片（Wan 5 秒），不用影視、綜藝片段。
- 卡通貼紙：grok-image（3 credits），提示詞末尾寫「plain solid pure green background」，然後摳綠：
  ```python
  green=(g>120)&(g-np.maximum(r,b)>40); alpha=MinFilter(3)+GaussianBlur(1); 綠溢色：g=min(g,max(r,b)); 裁 bbox
  ```

## 5. 合成與出片

1. `build_timeline.py episode.json voice/timings.json <public> --assets assets.json --host host.json --bgm music/bgm.mp3 --badge "AI 生成數位人演示 · 非商用"`
   - 片段演示用 `--from c01 --to c11`，或另存一個只含部分拍的 episode。
   - 卡片 `until: "<cue>"` 讓它在某個卡點消失。
2. 抽幀：`npx remotion still Episode out/x.jpg --frame=N`（並行 6–8 張拼一張圖看）；一定要看主播縮放的過渡中間幀。
3. 渲染：`npx remotion render Episode out/raw.mp4 --concurrency=6`（1080p 約 0.25× 即時）。
4. 出片：`ffmpeg -i raw.mp4 -c:v libx264 -crf 21 -pix_fmt yuv420p -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart 成品.mp4`（引擎直出約 -22 LUFS，偏小）。

## 6. 踩過的坑
- 字幕斷句要按**原文標點**（對齊結果裡沒有標點）：build_timeline 用 timings 的 text + chars。
- Renoise 下載 CDN 偶發中斷（curl 18）：逐個 `curl -C - --retry 3` 循環，下完 ffprobe 校驗。
- Wan 片段 480p 拉到 1080p 會軟；全螢幕鏡頭優先 Grok 720p。
- PiP 圓形頭像：face 座標填人臉在定妝照裡的相對位置（示例 [0.5, 0.33]）。
- PIL / numpy 只在 python3.14 裡有；ffmpeg 沒有 drawtext，標註一律用 PIL。
- 不要掃描系統找 API key；只讀 ~/.config/xiaolin-explainer/keys.env。
