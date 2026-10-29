#!/usr/bin/env python3
"""口播稿 → 分段任务（grok_generate.py 或 comfy_generate.py 的输入）+ 额度 / 耗时估算。

用法：
  python3 build_tasks.py script.json out_tasks.json [--backend grok|comfy] [--purpose "teaching a beginner tutorial step by step"] [--all-720p]

script.json：[{"id": "s1", "shot": "full|pip|vlog", "t": "这一段要念的台词", "host": "tank|me", "lang": "Mandarin Chinese|English|Japanese|…", "ref": "可选：这一段改用的参考图", "audio": "comfy 后端必填：这一段的音轨", "gesture": "可选：liyifan|qiuzhi|muzi|xiaolin|dashi"}, ...]
- host：tank = 白背心数字人（9:16，默认）；me = 用户本人数字人（16:9，persona.json → other_hosts.me）
- gesture：这一段用 persona.json 手势库（gestures.styles）里的哪一种；没写的 full 段用 gestures.default，pip / vlog / depth 段沿用 acts。用法见 SKILL.md 第 1 步
- lang：不写就是普通话；外语段台词直接写目标语言
- ref：进场景的段落（先用 grok image_edit 合成好的开场画面），不写就用主播的参考图
- 每段时长 = ceil(汉字和数字 / 5.4 + 英文词数 / 2.6 + 1.0)，夹在 4–15 秒（Grok 单段上限 15 秒；5.4 字/秒是实测语速，中英混杂的句子英文按词算）
- full 段 720p，pip 段 480p（画中画里看不出差别）；--all-720p 全部 720p
- 声音：persona.json 的 voice.preset（第二位主播是 other_hosts.me.voice_preset）填了内置音色名，任务就带 "voices"，提示词用 <AUDIO_0>；null 就照 desc 由 grok 配音
- 超过 15 秒的段会报错：先把台词拆短再跑
- --backend comfy：给 comfy_generate.py（ComfyUI 上的 MiniMax H3）。每段要写 "audio"（相对 script.json 的音轨：MiMo 克隆声或录音，见 references/voice.md），
  时长按音轨算，参考图当第一帧，提示词用 h3_prompt_template（不写台词，写了会烧字幕），不分 480p / 720p，也不占 grok 额度
提交前一定先把段数、秒数和预估占每周额度报给用户，等用户确认；comfy 后端报段数、秒数和预估耗时。
"""
import json, math, re, subprocess, sys
from pathlib import Path

EN_WPS = 2.6   # 英文约 2.6 词/秒
HERE = Path(__file__).resolve().parent.parent
P = json.loads((HERE / "persona.json").read_text())

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def main():
    src, dst = sys.argv[1], sys.argv[2]
    purpose = arg("--purpose", "explaining clearly")
    all720 = "--all-720p" in sys.argv
    backend = arg("--backend", "grok")
    if backend not in ("grok", "comfy"):
        sys.exit("--backend 只能是 grok 或 comfy")
    S = json.loads(Path(src).read_text())
    if backend == "comfy" and (missing := [s["id"] for s in S if not s.get("audio")]):
        sys.exit(f"comfy 后端每段都要有音轨（script.json 的 \"audio\"），缺：{', '.join(missing)}。音轨怎么做见 references/voice.md")
    tasks, lo, hi = [], 0.0, 0.0
    for s in S:
        lang = s.get("lang", "Mandarin Chinese")
        if backend == "comfy":
            audio = (Path(src).parent / s["audio"]).resolve()
            d = audio_seconds(audio)
        elif lang.startswith("Mandarin") or lang == "Chinese":
            d = math.ceil(mandarin_seconds(s["t"]) + 1.0)
        elif re.search(r"[぀-ヿ가-힯]", s["t"]):     # 日文 / 韩文：约 7 字/秒
            d = math.ceil(len(re.sub(r"\s", "", s["t"])) / 7 + 1.0)
        else:                                                    # 拉丁 / 阿拉伯等按词
            d = math.ceil(len(s["t"].split()) / EN_WPS + 1.0)
        if d > P["model"]["max_seconds"]:
            sys.exit(f"{s['id']} 约 {d:g} 秒，超过 15 秒：拆成两段再跑")
        shot = s.get("shot", "full")
        H = P["other_hosts"]["me"] if s.get("host", "tank") == "me" else None
        act = act_for(s, shot, H or P)
        if H:
            img = H["reference_image"]; ratio = H["ratio"]; preset = H.get("voice_preset")
            prompt = H["prompt_template"].format(ref="<IMAGE_0>", purpose=purpose, act=act, voice=voice_text(preset, H["voice"]), language=lang, line=s["t"])
        else:
            img = P["grok"]["reference_image"]; ratio = P["model"]["ratio"]; preset = P["voice"].get("preset")
            prompt = P["prompt_template"].format(ref="<IMAGE_0>", purpose=purpose, act=act, voice=voice_text(preset, P["voice"]["desc"]), line=s["t"]).replace("Mandarin Chinese", lang)
        img = Path(s.get("ref") or img)
        img = (img if img.is_absolute() else (Path(src).parent / img if s.get("ref") else HERE / img)).resolve()
        if not img.exists():
            sys.exit(f"{s['id']} 的参考图不存在：{img}（换形象见 references/new-avatar.md）")
        if backend == "comfy":
            prompt = (H or P)["h3_prompt_template"].format(purpose=purpose, act=act, language=spoken_language(lang, s["t"]))
            tasks.append({"id": s["id"], "prompt": prompt, "images": [str(img)], "audio": str(audio), "aspect_ratio": ratio, "duration": round(d, 2)})
            continue
        d = max(4, d)
        res = P["model"]["full_shot_resolution"] if (all720 or shot != "pip") else P["model"]["pip_shot_resolution"]
        pct = P["model"]["allowance_pct_per_second"].get(res) or P["model"]["allowance_pct_per_second"]["720p"]   # 480p 没实测，按 720p 估
        lo += d * pct[0]; hi += d * pct[1]
        task = {"id": s["id"], "prompt": prompt, "images": [str(img)], "aspect_ratio": ratio, "duration": d, "resolution_name": res}
        if preset: task["voices"] = [preset]
        tasks.append(task)
    Path(dst).write_text(json.dumps(tasks, ensure_ascii=False, indent=1))
    secs = sum(t["duration"] for t in tasks)
    if backend == "comfy":
        mins = secs * P["comfy"]["gen_sec_per_video_sec"] / 60
        print(f"{len(tasks)} 段 · 口播约 {secs:.0f} 秒 · ComfyUI 预估约 {mins:.0f} 分钟（10 秒一段实测约 186 秒，段越长越慢；不占 grok 额度）")
    else:
        print(f"{len(tasks)} 段 · 口播约 {secs} 秒 · 预估占 grok 每周额度 {lo:.0f}–{hi:.0f}%（720p 实测每秒 0.25–0.35%；480p 未实测，按 720p 估）")

def act_for(s, shot, host):
    """这一段的动作描述：写了 gesture 就用手势库那一种，没写的 full 段用手势库的 default，其他镜头沿用 acts。
    persona 没有 gestures 一节（旧版 persona）就一律用 acts。手势里的 {hands_rest} 换成这位主播的手平时放在哪里。"""
    G = P.get("gestures") or {}
    name = s.get("gesture") or (G.get("default") if shot == "full" else None)
    if not name:
        return P["acts"].get(shot, P["acts"]["full"])
    styles = G.get("styles", {})
    if name not in styles:
        sys.exit(f"{s['id']} 的 gesture「{name}」不在 persona.json 的 gestures.styles 里，可用：{', '.join(styles) or '（persona 没有手势库）'}")
    return styles[name].format(hands_rest=host["hands_rest"])

def mandarin_seconds(t):
    """普通话台词念多久：汉字和数字按 speed_cps 字/秒，夹杂的英文按词算，标点和省略号不算。
    中英混杂的句子不能把英文字母当汉字逐个算，不然会高估（27 字 + 10 个英文词原本算成 14 秒，实拍念 9.8 秒）"""
    zh = len(re.findall(r"[一-鿿0-9]", t))
    en = len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", t))
    return zh / P["voice"]["speed_cps"] + en / EN_WPS

def voice_text(preset, desc):
    """填进提示词「in {voice}」的那段：有内置音色就指向 <AUDIO_0>，没有就用文字描述的声音。"""
    return "the voice from <AUDIO_0>" if preset else f"a {desc}"

def audio_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r"[\d.]+", out):
        sys.exit(f"读不出音轨时长（文件不存在或不是音频）：{path}")
    return float(out)

def spoken_language(lang, t):
    """H3 提示词里的语言。普通话台词夹英文时写成试拍验证过的「Mandarin Chinese mixed with a few English phrases」。"""
    if (lang.startswith("Mandarin") or lang == "Chinese") and re.search(r"[A-Za-z]{2,}", t):
        return f"{lang} mixed with a few English phrases"
    return lang

if __name__ == "__main__":
    main()
