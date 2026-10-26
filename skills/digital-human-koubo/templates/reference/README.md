# 參考實現（C / D / E 三種風格）

這三個是做過的真實成品工程的剪輯程式碼（只有程式碼，不帶素材）。**內容每期都不一樣，所以不是填空模板**：起新工程後保留佈局、主播框、字幕、音效、過渡這些通用部分，按本期的稿子重寫每段的 Scene。

| 目錄 | 風格 | 出過的片 | 入口 | 時間軸 |
|---|---|---|---|---|
| launch-169 | C 發布解讀 | MemT 1.0 發布解讀（38 秒） | src/Film.tsx | src/timeline.json（逐字對齊 + 卡點） |
| tutorial-169 | D 保姆級教學 | AIGC 教學第二期（4 分 36 秒） | src/Tutorial.tsx | src/tl.json（nar 段 + 演示插入） |
| multihost-169 | E 多主播多語言 | AIGC 教學第三期（5 分 54 秒） | src/Tutorial.tsx | src/tl.json（nar / clip / title / outro） |

起工程：`bash scripts/new_edit.sh reference/tutorial-169 <工程目錄>`（會順帶放好 sfx 和配樂）。
素材檔名看程式碼裡的 `staticFile("…")`，按同樣的路徑放進 public/。

multihost-169/pipeline 是第三期從規劃到時間軸的腳本（plan → build_tasks → 技能的 `scripts/grok_generate.py tasks.json` → qa → build_tl），換聲統一用 `scripts/voicefx/unify.py`。跑 build_tasks 之前，主播參考圖放 `refs/`，場景段的開場畫面（grok 的 image_edit 合成）放 `stills/<段 id>.jpg`。
參考工程裡用包裝：import { PackLayer } from "./kit/registry"，見 references/packaging.md
