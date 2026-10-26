#!/usr/bin/env python3
"""口播稿 → grok CLI 分段任务（grok_generate.py 的输入）+ 每周额度估算。

用法：
  python3 build_tasks.py script.json out_tasks.json [--purpose "teaching a beginner tutorial step by step"] [--all-720p]

script.json：[{"id": "s1", "shot": "full|pip|vlog", "t": "这一段要念的台词", "host": "tank|me", "lang": "Mandarin Chinese|English|Japanese|…", "ref": "可选：这一段改用的参考图"}, ...]
- host：tank = 白背心数字人（9:16，默认）；me = 用户本人数字人（16:9，persona.json → other_hosts.me）
- lang：不写就是普通话；外语段台词直接写目标语言
- ref：进场景的段落（先用 grok image_edit 合成好的开场画面），不写就用主播的参考图
- 每段时长 = ceil(汉字和数字 / 5.4 + 英文词数 / 2.6 + 1.0)，夹在 4–15 秒（Grok 单段上限 15 秒；5.4 字/秒是实测语速，中英混杂的句子英文按词算）
- full 段 720p，pip 段 480p（画中画里看不出差别）；--all-720p 全部 720p
- 声音：persona.json 的 voice.preset（第二位主播是 other_hosts.me.voice_preset）填了内置音色名，任务就带 "voices"，提示词用 <AUDIO_0>；null 就照 desc 由 grok 配音
- 超过 15 秒的段会报错：先把台词拆短再跑
提交前一定先把段数、秒数和预估占每周额度报给用户，等用户确认。
"""
import json, math, re, sys
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
    S = json.loads(Path(src).read_text())
    tasks, lo, hi = [], 0.0, 0.0
    for s in S:
        lang = s.get("lang", "Mandarin Chinese")
        if lang.startswith("Mandarin") or lang == "Chinese":
            d = math.ceil(mandarin_seconds(s["t"]) + 1.0)
        elif re.search(r"[぀-ヿ가-힯]", s["t"]):     # 日文 / 韩文：约 7 字/秒
            d = math.ceil(len(re.sub(r"\s", "", s["t"])) / 7 + 1.0)
        else:                                                    # 拉丁 / 阿拉伯等按词
            d = math.ceil(len(s["t"].split()) / EN_WPS + 1.0)
        if d > P["model"]["max_seconds"]:
            sys.exit(f"{s['id']} 约 {d} 秒，超过 15 秒：拆成两段再跑")
        d = max(4, d)
        shot = s.get("shot", "full")
        res = P["model"]["full_shot_resolution"] if (all720 or shot != "pip") else P["model"]["pip_shot_resolution"]
        pct = P["model"]["allowance_pct_per_second"].get(res) or P["model"]["allowance_pct_per_second"]["720p"]   # 480p 没实测，按 720p 估
        lo += d * pct[0]; hi += d * pct[1]
        act = P["acts"].get(shot, P["acts"]["full"])
        if s.get("host", "tank") == "me":
            H = P["other_hosts"]["me"]; img = H["reference_image"]; ratio = H["ratio"]; preset = H.get("voice_preset")
            prompt = H["prompt_template"].format(ref="<IMAGE_0>", purpose=purpose, act=act, voice=voice_text(preset, H["voice"]), language=lang, line=s["t"])
        else:
            img = P["grok"]["reference_image"]; ratio = P["model"]["ratio"]; preset = P["voice"].get("preset")
            prompt = P["prompt_template"].format(ref="<IMAGE_0>", purpose=purpose, act=act, voice=voice_text(preset, P["voice"]["desc"]), line=s["t"]).replace("Mandarin Chinese", lang)
        img = Path(s.get("ref") or img)
        img = (img if img.is_absolute() else (Path(src).parent / img if s.get("ref") else HERE / img)).resolve()
        if not img.exists():
            sys.exit(f"{s['id']} 的参考图不存在：{img}（换形象见 references/new-avatar.md）")
        task = {"id": s["id"], "prompt": prompt, "images": [str(img)], "aspect_ratio": ratio, "duration": d, "resolution_name": res}
        if preset: task["voices"] = [preset]
        tasks.append(task)
    Path(dst).write_text(json.dumps(tasks, ensure_ascii=False, indent=1))
    secs = sum(t["duration"] for t in tasks)
    print(f"{len(tasks)} 段 · 口播约 {secs} 秒 · 预估占 grok 每周额度 {lo:.0f}–{hi:.0f}%（720p 实测每秒 0.25–0.35%；480p 未实测，按 720p 估）")

def mandarin_seconds(t):
    """普通话台词念多久：汉字和数字按 speed_cps 字/秒，夹杂的英文按词算，标点和省略号不算。
    中英混杂的句子不能把英文字母当汉字逐个算，不然会高估（27 字 + 10 个英文词原本算成 14 秒，实拍念 9.8 秒）"""
    zh = len(re.findall(r"[一-鿿0-9]", t))
    en = len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", t))
    return zh / P["voice"]["speed_cps"] + en / EN_WPS

def voice_text(preset, desc):
    """填进提示词「in {voice}」的那段：有内置音色就指向 <AUDIO_0>，没有就用文字描述的声音。"""
    return "the voice from <AUDIO_0>" if preset else f"a {desc}"

if __name__ == "__main__":
    main()
