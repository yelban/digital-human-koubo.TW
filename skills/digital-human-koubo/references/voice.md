# 换声音

默认用 Grok 原生配音（persona.json 里的 voice.desc，每段一字不改，整片音色才统一）。

## 换成自己的声音（MiMo 克隆）
- 录 12–20 秒干净的朗读（安静房间、离嘴 20 厘米），发给 Claude Code，说「用我的声音配这段话」。
- Claude 调用小米 MiMo：`mimo-v2.5-tts-voiceclone`，assistant 消息放正文，user 消息放语气说明；密钥只放在 ~/.config/ai-teardown/mimo.env。
- 克隆声 2–5 kHz 偏弱，配完套 EQ+压缩（SKILL.md 里的人声链）。
- 只克隆本人或明确授权的声音。

## 按文字设计音色
- `mimo-v2.5-tts-voicedesign`：user 消息写音色描述（如「温柔知性的年轻女声，语速稍慢，咬字清楚」），不能为空。

## 让数字人用新声音开口
Grok 只吃图片，不吃音频，口型跟的是它自己的配音。grok CLI 没有「音频驱动口型」的模式，所以要口型对上自己的声音：
- 另外用支持音频驱动的服务（例如 Wan 3.0、OmniHuman；这个技能目前没接）。
- 或者只在画中画、空镜段落用新声音做旁白，全屏出镜段保留 Grok 原声。
- grok 的 reference_to_video 还能指定预设音色（`voices`，例如 eve、ara），让每段同一个声音；中文效果没测过，build_tasks.py 目前没接。
