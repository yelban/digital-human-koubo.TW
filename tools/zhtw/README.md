# 繁體中文化工具

這個 fork 有兩個分支：

- **`simplified`**：上游 [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo) 加上本 fork 的功能修改（grok CLI 後端等），文字維持簡體。上游更新合併進這裡。
- **`main`**：由 `zhtw.py build` 從 `simplified` 整份產生的繁體版，台灣用語。GitHub 預設分支，安裝技能用這個。

**不要直接改 `main`。** 下次產生時會被蓋掉，所以 `build` 發現 `main` 上有手動 commit 就會停下來。要改技能內容或程式，在 `simplified` 用簡體改；要改繁體的用字，改 `phrases.tsv`。

## 指令

在 repo 根目錄、`simplified` 分支上執行。需要 opencc（`brew install opencc`）。

| 指令 | 做什麼 |
|---|---|
| `python3 tools/zhtw/zhtw.py sync` | 抓上游 → 合併進 `simplified` → `build`。合併有衝突就停下，解決並 commit 後再跑 `build` |
| `python3 tools/zhtw/zhtw.py build` | 轉換 `simplified` 的內容，在 `main` 上產生一個新 commit（兩個 parent：前一版 `main` 和 `simplified`） |
| `python3 tools/zhtw/zhtw.py terms` | 列出 opencc 用台灣詞彙換掉的詞，預設只看上次 build 之後改過的檔案。換錯的就加進 `phrases.tsv` |
| `python3 tools/zhtw/zhtw.py convert <目錄>` | 只轉換一個目錄，不碰 git，試轉換用 |

產生完用 `git push origin simplified main` 推上去。

## 上游更新時

1. `git switch simplified`，再跑 `python3 tools/zhtw/zhtw.py sync`。
2. 有衝突時，衝突只會出現在本 fork 改過的地方（grok 後端那些檔案），照簡體解決。
3. 跑 `python3 tools/zhtw/zhtw.py terms`，看新加的文字有沒有被轉錯的詞，有就補 `phrases.tsv`、commit，再 `build`。
4. `git diff main^1 main` 看這次產生的差異，沒問題就 push。

## 轉換規則

- **範圍**：`skills/` 底下的文件、JSON、TS／TSX。`.py`、`.sh`、`.swift` 不轉，因為程式要拿文字跟 whisper 的簡體輸出比對；例外是 `zhtw.py` 裡 `CONTENT_PY` 列的兩支，它們的中文是成片內容。`README.zh-CN.md` 轉成新的 `README.zh-TW.md`，`README.md` 和 `README.zh-CN.md` 只加繁體連結。
- **順序**：日文（含假名的片段）先保護起來不轉 → `phrases.tsv` 的詞組換成指定寫法 → opencc `s2twp` → 「臺」改「台」（平台、台詞）→ 含中文的 “” 改「」、‘’ 改『』 → 簡體字型換成繁體字型（PingFang SC → PingFang TC 等）。
- **檢查**（沒過就不產生 commit）：
  - 有 `chars` 的時間軸段落，`text` 長度不能變。
  - 花字錨點（`edit.json` 的「段號:詞」）轉換後位置不變。
  - 檔名含中文的檔案，轉換後還引用得到。
  - 程式檔去掉中文、全形標點和字型名稱之後，轉換前後要一樣。

## 沒處理的

- 圖片裡的簡體字：`assets/styles/*.jpg`、`assets/packaging/` 的預覽圖、`docs/` 的 GIF 與封面。
- grok 念繁體稿的效果還沒實測。
