# 換聲音

預設用 Grok 原生配音（persona.json 裡的 voice.desc，每段一字不改，整片音色才統一）。

## 換成自己的聲音（MiMo 克隆）
- 錄 12–20 秒乾淨的朗讀（安靜房間、離嘴 20 公分），發給 Claude Code，說「用我的聲音配這段話」。
- Claude 呼叫小米 MiMo：`mimo-v2.5-tts-voiceclone`，assistant 訊息放正文，user 訊息放語氣說明；金鑰只放在 ~/.config/ai-teardown/mimo.env。
- 克隆聲 2–5 kHz 偏弱，配完套 EQ+壓縮（SKILL.md 裡的人聲鏈）。
- 只克隆本人或明確授權的聲音。

## 按文字設計音色
- `mimo-v2.5-tts-voicedesign`：user 訊息寫音色描述（如「溫柔知性的年輕女聲，語速稍慢，咬字清楚」），不能為空。

## 讓數位人用新聲音開口
Grok 只吃圖片，不吃音訊，口型跟的是它自己的配音。grok CLI 沒有「音訊驅動口型」的模式，所以要口型對上自己的聲音：
- 另外用支援音訊驅動的服務（例如 Wan 3.0、OmniHuman；這個技能目前沒接）。
- 或者只在畫中畫、空鏡段落用新聲音做旁白，全螢幕出鏡段保留 Grok 原聲。
- grok 的 reference_to_video 還能指定預設音色（`voices`，例如 eve、ara），讓每段同一個聲音；中文效果沒測過，build_tasks.py 目前沒接。
