#!/usr/bin/env python3
"""tasks.json → grok CLI 逐段生成口播片段（reference_to_video，Grok Imagine Video 1.5）→ gen/<段 id>.mp4。

用法：python3 grok_generate.py tasks.json [--out gen] [--only s1,s3] [--timeout 600]
- tasks.json 由 build_tasks.py 生成：[{"id","prompt","images":[绝对路径],"aspect_ratio","duration","resolution_name","voices":[内置音色名，可选]}, ...]
- 前提：grok 已登录；grok 里 /privacy 是 Opt in（ZDR 关着），否则视频工具直接报错
- 串行生成，每段约 1–1.5 分钟；gen/<id>.mp4 已存在且能解码就跳过，要重拍就删掉那个文件
- grok 以 gen/.grok/ 为工作目录，里面只放参考图，不把整个工程暴露给 grok
- 只开放 reference_to_video：init 消息里多出别的工具就在模型动手前杀掉进程，提示把新工具名补进 DISALLOWED
- 工具由 grok 的模型代为调用：生成后核对它实际传的参数，和任务不一致的段标 ⚠
- 用掉的是 grok 每周额度，跑完去 grok 里看 /usage
"""
import json, os, shutil, subprocess, sys, threading
from pathlib import Path

# grok 1.0.70 的内置工具里除 reference_to_video 以外的全部。grok 升级后被 init 守卫拦下时，把它报出的工具名补进来。
DISALLOWED = ("run_terminal_command,read_file,search_replace,list_dir,grep,kill_command_or_subagent,todo_write,"
              "get_command_or_subagent_output,spawn_subagent,scheduler_create,scheduler_delete,scheduler_list,monitor,"
              "search_tool,use_tool,workflow,enter_plan_mode,exit_plan_mode,ask_user_question,send_feedback,web_search,"
              "web_fetch,image_gen,image_edit,image_to_video,write")
GROK = os.environ.get("GROK_BIN") or shutil.which("grok") or os.path.expanduser("~/.grok/bin/grok")

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def main():
    tasks = json.loads(Path(sys.argv[1]).read_text())
    out = Path(arg("--out", "gen")); work = (out / ".grok").resolve(); work.mkdir(parents=True, exist_ok=True)
    only = set(arg("--only", "").split(",")) - {""}
    timeout = int(arg("--timeout", "600"))
    failed = []
    for t in tasks:
        if only and t["id"] not in only: continue
        dst = out / f"{t['id']}.mp4"
        if dst.exists() and decodes(dst):
            print(f"  {t['id']:5s} 已有 {dst}，跳过"); continue
        t = stage_images(t, work)
        path, used, err = run_grok(t, work, timeout)
        if err:
            failed.append(t["id"]); print(f"✗ {t['id']:5s} {err}"); continue
        shutil.copyfile(path, dst)
        bad = mismatches(t, used)
        print(f"{'⚠' if bad else ' '} {t['id']:5s} {duration(dst):.2f} 秒 → {dst}" + (f"  grok 传的参数和任务不一致：{', '.join(bad)}" if bad else ""))
    print("跑完了。去 grok 里输入 /usage 看本周额度用掉多少。" + (f" 失败的段：{', '.join(failed)}" if failed else ""))
    sys.exit(1 if failed else 0)

def stage_images(t, work):
    """参考图复制进 grok 的工作目录，任务里的路径改成那里的绝对路径。"""
    imgs = []
    for i, src in enumerate(t["images"]):
        p = work / f"ref{i}_{Path(src).name}"
        shutil.copyfile(src, p); imgs.append(str(p))
    return {**t, "images": imgs}

def instruction(t):
    return ("Call the reference_to_video tool exactly once with the arguments below, passing the prompt text verbatim. "
            "Do not call any other tool and do not retry. After the tool returns, reply with only the saved video path.\n\n"
            f"images: {json.dumps(t['images'], ensure_ascii=False)}\n"
            f"aspect_ratio: {json.dumps(t['aspect_ratio'])}\n"
            f"duration: {t['duration']}\n"
            f"resolution_name: {json.dumps(t['resolution_name'])}\n"
            + (f"voices: {json.dumps(t['voices'])}\n" if t.get("voices") else "")
            + f"prompt:\n{t['prompt']}")

def run_grok(t, work, timeout):
    """跑一段，回传 (视频路径, grok 实际传的参数, 错误说明)。"""
    p = subprocess.Popen([GROK, "-p", instruction(t), "--cwd", str(work), "--max-turns", "3",
                          "--disallowed-tools", DISALLOWED, "--deny", "Bash", "--deny", "MCPTool", "--deny", "WebFetch",
                          "--output-format", "streaming-messages-json"],
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    timer = threading.Timer(timeout, p.kill); timer.start()
    used = result = None
    try:
        for line in p.stdout:
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("subtype") == "init" and m.get("tools") != ["reference_to_video"]:
                p.kill()
                extra = [x for x in m.get("tools", []) if x != "reference_to_video"]
                sys.exit(f"grok 开放的工具不只 reference_to_video，已中止（还没生成）。把这些名字补进 grok_generate.py 的 DISALLOWED 再跑：{','.join(extra)}")
            for c in (m.get("message") or {}).get("content") or []:
                if c.get("type") == "tool_use" and c.get("name") == "reference_to_video": used = c.get("input")
                if c.get("type") == "tool_result": result = c.get("content")
    finally:
        timer.cancel(); p.kill(); p.wait()
    if result is None:
        return None, used, f"{timeout} 秒内没拿到结果（超时或 grok 没调用工具）"
    if isinstance(result, list): result = "".join(c.get("text", "") for c in result if isinstance(c, dict))
    try: r = json.loads(result)
    except ValueError: r = {"message": str(result)}
    if r.get("path") and Path(r["path"]).exists():
        return r["path"], used, None
    msg = r.get("message") or str(r)
    if "zero data retention" in msg.lower():
        sys.exit("grok 的 ZDR（零数据保留）开着，视频工具不可用。请用户在 grok 里输入 /privacy 改成 Opt in 再跑；做完提醒改回 Opt out。")
    return None, used, msg if "voice" in msg.lower() else msg[:300]   # 音色名错误时，可用清单在错误消息后半段

def mismatches(t, used):
    if not used: return ["没看到 grok 的工具调用记录"]
    bad = [k for k in ("aspect_ratio", "duration", "resolution_name", "images") if used.get(k) != t[k]]
    if (used.get("voices") or []) != (t.get("voices") or []): bad.append("voices")
    if (used.get("prompt") or "").strip() != t["prompt"].strip(): bad.append("prompt")
    return bad

def decodes(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    return r.returncode == 0 and not r.stderr.strip()

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out or 0)

if __name__ == "__main__":
    main()
