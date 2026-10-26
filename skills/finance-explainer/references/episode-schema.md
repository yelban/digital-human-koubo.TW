# 拍表與配置檔案欄位

## episode.json
```json
{
  "meta": {"title": "…", "channel": "Berry說", "theme": "v2-glass", "fps": 30, "width": 1920, "height": 1080, "facts": "facts.md"},
  "voice": {"engine": "mimo", "model": "mimo-v2.5-tts", "voice": "茉莉", "style": "（佔位）語氣說明…"},
  "lexicon": {"GPU": "G P U", "H20": "H 二十"},
  "beats": [
    {"id": "c01", "narration": "二〇二五年一月二十七號，[[n1]]輝達一天之內…", "host": "off", "bg": "gen:trading_floor",
     "overlays": [{"type": "counter", "at": "n1", "from": 0, "to": 600000000000, "prefix": "−$", "money": true, "pos": "center"}]},
    {"id": "c05", "kind": "chapter", "duration": 2.6, "bg": "gen:chip_macro", "title": "第一章 · 卡了什麼", "subtitle": "EXPORT CONTROLS"},
    {"id": "c10", "narration": "…", "host": "pip",
     "stage": {"type": "steps", "title": "2024.12 管制升級", "source": "美國商務部 BIS 公告", "items": [{"at": "f1", "text": "24 類晶片製造裝置", "sub": "造不出來"}]}}
  ]
}
```

### 拍（beat）
| 欄位 | 說明 |
|---|---|
| id | 唯一，錄音稿和音訊檔案都用它 |
| narration | 口播原文；`[[cue]]` 標卡點（小寫字母開頭） |
| kind | `chapter` 章節卡（無口播，用 duration、title、subtitle、bg） |
| host | `full` / `shrink` / `side` / `pip` / `off`（切換時主播彈簧縮放） |
| punch | 僅 full：推近倍數（1.08–1.15），繞臉部放大，蓋跳切 |
| bg | host=off 時的全螢幕空鏡，`gen:<id>` / `stock:<id>` 在 assets.json 查 |
| stage | 舞台卡片（host=pip 時用），見下 |
| overlays | 疊加卡片陣列，見下 |

### 疊加卡片（overlays）通用欄位
`type`、`at`（cue 名或 "start"）、`until`（可選，到某 cue 消失；預設拍結束）、`pos`（left / right / lower / center / topleft）。

| type | 專有欄位 |
|---|---|
| comment | user, text, side(left/right), time |
| datestack | items: [{at, date, label, strike}] |
| counter | from, to, prefix, suffix, money, dur |
| kinetic | text, sub, style(big/stamp/stamp-red/brush), size |
| term | en, zh |
| questions | items: [問題…] |
| meme | src(gen:id), caption |
| sticker | src(gen:id), bubble: [{at, text}] |
| list | items: [{at, text, tone(good/bad)}] |

### 舞台（stage）
| type | 欄位 |
|---|---|
| bars | title, source, bars: [{label(可含\n), value, unit, at, hot}], callout {at, text} |
| line | title, source, points [{x, y}], reveal [cue…], callout |
| steps | title, source, items [{at, text, sub}] |
| doc | source（「據 XX 公告整理」）, title, lines [{at, text, hl}] |
| quiz | question, ask, reveal(cue), answer, note |

## host.json
```json
{"src": "host/anchor.jpg", "kind": "image", "face": [0.5, 0.33], "offset": 0.23, "loop_len": 10,
 "clips": {"c02": "host/c02.mp4", "c03": {"src": "host/grok_15s.mp4", "offset": 9.08}},
 "loops": ["host/loopA.mp4", "host/loopB.mp4", "host/loopC.mp4"]}
```
- clips 值為字串時用全域 offset（Wan = 0.23）；為對象時用自己的 offset（Grok = 片段內畫面起點）。
- 沒有 clip 的可見拍用 loops 輪換（長拍自動拆成 ≤ loop_len−0.5 秒的段）。

## assets.json
`{"trading_floor": {"src": "assets/trading_floor.mp4", "kind": "video"}, "sticker_gpu": {"src": "assets/sticker_gpu.png", "kind": "image"}}`
缺失的素材在畫面上畫「素材待生成」佔位，樣片階段也能先渲染看節奏。

## timings.json（三個來源同格式）
narrate_mimo.py（佔位）/ align_recording.py（自錄）/ grok_beats.py（Grok 原生說話）：
`beats[id] = {file, text, start, end, duration, words[{text,start,end,i0,i1}], chars[每個字的開始秒], cues{name: 秒}, align}`
