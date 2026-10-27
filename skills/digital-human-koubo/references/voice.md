# 换声音

默认用 Grok 原生配音（persona.json 里的 voice.desc，每段一字不改，整片音色才统一）。

## 用 grok 内置音色
grok 按 desc 配音时，每段的声音可能有细微差别。要每段固定同一个声音，就指定内置音色：
- persona.json 的 `voice.preset` 填音色名（第二位主播填 `other_hosts.me.voice_preset`），例如 `"eve"`。null = 照 desc 配音。
- build_tasks.py 会在任务里带 `"voices": ["eve"]`，提示词的声音描述改成 `the voice from <AUDIO_0>`；grok_generate.py 会核对 grok 实际传的音色。
- 可用的名字（2026-10-27 用不存在的音色名问 grok 拿到的清单）：ara、eve、leo、rex、sal、carina、zagan、helix、orion、luna、iris、altair、zenith、perseus、helios、lux、kepler、rigel、cosmo、celeste、ursa、sirius、lumen、castor、naksh、atlas。名字填错时，grok_generate.py 会印出最新清单。
- xAI 文档说每个音色都能说所有支持的语言，中文只有一个语言代码 `zh`，没有地区口音的选项；eve、leo 标的是英国腔。官方没写性别，中文听起来怎样也没测过：先拍第 1 段给用户听，再批量。
- 自己的声音：grok 的错误消息说 `/v1/custom-voices` API 建的自定义音色也能用，但要 xAI API 密钥，这个技能没接、也没测过。

## 换成自己的声音（MiMo 克隆）
- 录 12–20 秒干净的朗读（安静房间、离嘴 20 厘米），发给 Claude Code，说「用我的声音配这段话」。
- Claude 调用小米 MiMo：`mimo-v2.5-tts-voiceclone`，assistant 消息放正文，user 消息放语气说明；密钥只放在 ~/.config/ai-teardown/mimo.env。
- 克隆声 2–5 kHz 偏弱，配完套 EQ+压缩（SKILL.md 里的人声链）。
- 只克隆本人或明确授权的声音。

## 按文字设计音色
- `mimo-v2.5-tts-voicedesign`：user 消息写音色描述（如「温柔知性的年轻女声，语速稍慢，咬字清楚」），不能为空。

## 让数字人用新声音开口
Grok 只吃图片，不吃音频，口型跟的是它自己的配音。grok CLI 没有「音频驱动口型」的模式，所以要口型对上自己的声音：
- 用 comfy 后端：ComfyUI 上的 MiniMax H3 锁住给定的音轨、只生成画面（scripts/comfy_generate.py）。先把每段配好音存成文件，在 script.json 那段写 `"audio"`，再 `build_tasks.py --backend comfy`。2026-10-27 用 grok luna 的音轨试拍，口型用户看过可以接受。
- 或者只在画中画、空镜段落用新声音做旁白，全屏出镜段保留 Grok 原声。
