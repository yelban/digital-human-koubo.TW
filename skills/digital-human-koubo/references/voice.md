# 換聲音

預設用 Grok 原生配音（persona.json 裡的 voice.desc，每段一字不改，整片音色才統一）。

## 用 grok 內建音色
grok 按 desc 配音時，每段的聲音可能有細微差別。要每段固定同一個聲音，就指定內建音色：
- persona.json 的 `voice.preset` 填音色名（第二位主播填 `other_hosts.me.voice_preset`），例如 `"eve"`。null = 照 desc 配音。
- build_tasks.py 會在任務裡帶 `"voices": ["eve"]`，提示詞的聲音描述改成 `the voice from <AUDIO_0>`；grok_generate.py 會核對 grok 實際傳的音色。
- 可用的名字（2026-10-27 用不存在的音色名問 grok 拿到的清單）：ara、eve、leo、rex、sal、carina、zagan、helix、orion、luna、iris、altair、zenith、perseus、helios、lux、kepler、rigel、cosmo、celeste、ursa、sirius、lumen、castor、naksh、atlas。名字填錯時，grok_generate.py 會印出最新清單。
- xAI 文件說每個音色都能說所有支援的語言，中文只有一個語言代碼 `zh`，沒有地區口音的選項；eve、leo 標的是英國腔。官方沒寫性別，中文聽起來怎樣也沒測過：先拍第 1 段給使用者聽，再批次。
- 自己的聲音：grok 的錯誤訊息說 `/v1/custom-voices` API 建的自訂音色也能用，但要 xAI API 金鑰，這個技能沒接、也沒測過。

## 換成自己的聲音（MiMo 克隆）
- 錄 12–20 秒乾淨的朗讀（安靜房間、離嘴 20 公分），發給 Claude Code，說「用我的聲音配這段話」。
- Claude 呼叫小米 MiMo：`mimo-v2.5-tts-voiceclone`，assistant 訊息放正文，user 訊息放語氣說明；金鑰只放在 ~/.config/ai-teardown/mimo.env。
- 克隆聲 2–5 kHz 偏弱，配完套 EQ+壓縮（SKILL.md 裡的人聲鏈）。
- 只克隆本人或明確授權的聲音。

## 台灣腔配音（CosyVoice 3，comfy 後端用）
- `python3 scripts/tts_generate.py script.json`：經 ssh 到 GPU 機器（persona.json 的 tts 那一節，環境變數 TTS_SSH_HOST 優先）跑 CosyVoice 3 零樣本克隆，存成 `audio/<段 id>.wav` 並寫回 `"audio"`。機器上的環境怎麼裝見 references/install.md。
- 克隆的是主播的參考音檔：persona.json → voice.tts_ref（使用者本人主播是 other_hosts.me.tts_ref），10–30 秒乾淨朗讀加逐字稿。倉庫裡沒有這些檔案，只放在本機技能目錄。只克隆本人或明確授權的聲音；拿 AI 成品（grok、Gemini 的配音）當參考是否合乎服務條款沒查過，只能測試用。
- 2026-10-29 在 RTX 3090 Ti 試聽：CosyVoice 3 比 VoxCPM2、IndexTTS-2.5、BlueMagpie-TTS 自然，3 段約 26 秒配完。用拼音強改平舌、輕聲改本調，捲舌少了，但使用者聽起來太刻意，所以台詞照原文送。
- 個別詞唸錯時，在那段加 `"tts_text"` 改送進 TTS 的文字，字幕和回聽仍對照 `"t"`。
- 和 comfy_generate.py 共用同一張顯示卡，配完音再生成畫面，兩個不要同時跑。

## 按文字設計音色
- `mimo-v2.5-tts-voicedesign`：user 訊息寫音色描述（如「溫柔知性的年輕女聲，語速稍慢，咬字清楚」），不能為空。

## 讓數位人用新聲音開口
Grok 只吃圖片，不吃音訊，口型跟的是它自己的配音。grok CLI 沒有「音訊驅動口型」的模式，所以要口型對上自己的聲音：
- 用 comfy 後端：ComfyUI 上的 MiniMax H3 鎖住給定的音軌、只生成畫面（scripts/comfy_generate.py）。先把每段配好音（tts_generate.py，或自己放音軌），在 script.json 那段寫 `"audio"`，再 `build_tasks.py --backend comfy`。2026-10-27 用 grok luna 的音軌試拍，口型使用者看過可以接受。
- 或者只在畫中畫、空鏡段落用新聲音做旁白，全螢幕出鏡段保留 Grok 原聲。
