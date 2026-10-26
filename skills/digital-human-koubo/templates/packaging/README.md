# 包裝元件庫 + 圖鑑工程

- `src/kit/`：47 個包裝元件（core 底座、Annotate 標註、Text 文字、Overlay 疊加、Map 地圖、Wangan 網感、Explain 解說、Beast 節奏、Polish 質感）+ `registry.tsx`（按名字呼叫，`PackLayer`）。
- `src/demos/Demos.tsx`：每個元件一段 3–5 秒演示；`Gallery` 合成把它們首尾相接。
- 用法和參數：`../../references/packaging.md`；手法依據：`../../references/packaging-playbook.md`。

在別的工程裡用：把 `src/kit/` 整個複製過去（`new_edit.sh` 起的 huazi-916 已經帶了），`import { PackLayer } from "./kit/registry"`。
地圖元件依賴 d3-geo、topojson-client、world-atlas（package.json 已寫）。

重渲圖鑑：演示用到 `public/media/` 裡的素材（數位人口播 host_h.mp4 / host_v.mp4、場景圖 shop/ad/travel/class/cat/dog.jpg、截圖 screen.png / doc.png），打包版不帶這些個人素材，換成你自己的同名檔案後：
```bash
npx remotion render src/index.ts Gallery out/圖鑑.mp4 --concurrency=6
```
