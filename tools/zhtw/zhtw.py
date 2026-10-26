#!/usr/bin/env python3
"""把 simplified 分支（上游 + 本 fork 的功能修改，簡體）轉成 main 分支（繁體，台灣用語）。

用法（在 repo 根目錄）：
  python3 tools/zhtw/zhtw.py sync             抓上游 → 合併進 simplified → build
  python3 tools/zhtw/zhtw.py build            用 simplified 的內容重新產生 main（main 不手改）
  python3 tools/zhtw/zhtw.py convert <目錄>    只轉換一個目錄，不碰 git（試轉換用）
  python3 tools/zhtw/zhtw.py terms [檔案…]     列出 opencc 自己換掉的詞，檢查要不要補 phrases.tsv
                                              （不給檔案就看上次 build 之後 simplified 改過的檔案）

需要 opencc（brew install opencc）。流程說明見同目錄的 README.md。
"""
import difflib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE, TARGET, UPSTREAM = "simplified", "main", "upstream/main"
TRAILER = "Zhtw-Source"
SCOPE = "skills/"
SKIP_SUFFIX = (".py", ".sh", ".swift")   # 程式會拿文字跟 whisper 的簡體輸出比對，維持簡體
CONTENT_PY = {   # 例外：這幾支的中文是成片內容（台詞、章節名），要跟轉好的 tl.json、Tutorial.tsx 一致
    "skills/digital-human-koubo/templates/reference/multihost-169/pipeline/plan.py",
    "skills/digital-human-koubo/templates/reference/multihost-169/pipeline/build_tl.py",
}
HAN = re.compile(r"[一-鿿]")
PUA = re.compile(r"[-]")
JAPANESE = re.compile(r"[^\x00-\x7f\s]*[ぁ-ゖァ-ヺ][^\x00-\x7f\s]*")   # 含假名的一段，裡面的漢字是日文，不轉
FONTS = [('"Kaiti SC"', '"Kaiti TC","BiauKaiTC"'), ("Kaiti SC", "Kaiti TC"), ("PingFang SC", "PingFang TC"),
         ("Hiragino Sans GB", "Heiti TC"), ("Songti SC", "Songti TC"), ("Noto Serif SC", "Noto Serif TC"), ("Noto Sans SC", "Noto Sans TC")]
LANG_EN = "**English** · [简体中文](README.zh-CN.md)"
LANG_CN = "[English](README.md) · **简体中文**"
LANG_TW = "[English](README.md) · [简体中文](README.zh-CN.md) · **繁體中文**"
CLONE = ("git clone https://github.com/andyhuo520/digital-human-koubo.git\ncd digital-human-koubo\n",
         "git clone https://github.com/yelban/digital-human-koubo.TW.git\ncd digital-human-koubo.TW\n")
FORK_NOTE = ("> 這是 [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo) 的繁體中文版，"
             "影片生成改用 grok CLI。內容由 `tools/zhtw/zhtw.py` 從 `simplified` 分支自動轉換。")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sync": sync()
    elif cmd == "build": build()
    elif cmd == "convert" and len(sys.argv) == 3: convert_tree(Path(sys.argv[2]))
    elif cmd == "terms": terms(sys.argv[2:])
    else: sys.exit(__doc__)


# ---------- 轉換 ----------

def load_phrases():
    rows = []
    for line in (HERE / "phrases.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            s, t = line.split("\t")[:2]; rows.append((s, t))
    return sorted(rows, key=lambda r: -len(r[0]))


def opencc(cfg, text):
    return subprocess.run(["opencc", "-c", cfg], input=text, capture_output=True, text=True, check=True).stdout


def protect(text, phrases):
    """自訂詞組先換成私用區字元，opencc 會原樣留著，轉完再換成指定的繁體。"""
    if PUA.search(text): raise ValueError("原文含私用區字元，無法保護自訂詞組")
    keep = {}
    for j, ja in enumerate(sorted(set(JAPANESE.findall(text)), key=len, reverse=True)):   # 先保護日文，詞組才不會換到日文裡
        ph = chr(0xF000 + j); keep[ph] = ja; text = text.replace(ja, ph)
    for i, (s, t) in enumerate(phrases):
        if s in text:
            ph = chr(0xE000 + i); keep[ph] = t; text = text.replace(s, ph)
    return text, keep


def to_tw(text, phrases):
    text, keep = protect(text, phrases)
    text = opencc("s2twp", text).replace("臺", "台")   # 台灣慣用「平台」「台詞」
    for ph, t in keep.items(): text = text.replace(ph, t)
    text = re.sub(r"‘([^‘’\n]*[一-鿿][^‘’\n]*)’", r"『\1』", text)
    text = re.sub(r"“([^“”\n]*[一-鿿][^“”\n]*)”", r"「\1」", text)
    for a, b in FONTS: text = text.replace(a, b)
    return text


def in_scope(p, root):
    return p.is_file() and (p.suffix not in SKIP_SUFFIX or p.relative_to(root).as_posix() in CONTENT_PY)


def read(p):
    return p.read_bytes().decode("utf-8")   # 不走 read_text，保留原本的換行字元


def convert_tree(root):
    """把 root（一份 repo 的檔案）裡的 skills/ 轉成繁體，並產生 README.zh-TW.md。回傳改過的檔案。"""
    phrases, changed = load_phrases(), []
    for p in sorted((root / SCOPE).rglob("*")):
        if not in_scope(p, root): continue
        try: s = read(p)
        except UnicodeDecodeError: continue
        if not HAN.search(s) and not any(a in s for a, _ in FONTS): continue
        t = to_tw(s, phrases)
        if t != s: p.write_bytes(t.encode("utf-8")); changed.append(p.relative_to(root))
    en, cn = root / "README.md", root / "README.zh-CN.md"
    s_en, s_cn = read(en), read(cn)
    for s, needle in ((s_en, LANG_EN), (s_cn, LANG_CN), (s_cn, CLONE[0])):
        if needle not in s: raise ValueError(f"README 找不到要替換的這段，上游可能改了格式，請更新 zhtw.py：{needle!r}")
    tw = to_tw(s_cn, phrases).replace(to_tw(LANG_CN, phrases), LANG_TW + "\n\n" + FORK_NOTE, 1).replace(CLONE[0], CLONE[1])
    (root / "README.zh-TW.md").write_bytes(tw.encode("utf-8"))
    en.write_bytes(s_en.replace(LANG_EN, LANG_EN + " · [繁體中文](README.zh-TW.md)", 1).encode("utf-8"))
    cn.write_bytes(s_cn.replace(LANG_CN, LANG_CN + " · [繁體中文](README.zh-TW.md)", 1).encode("utf-8"))
    print(f"轉換了 {len(changed)} 個檔案，另產生 README.zh-TW.md")
    return changed


# ---------- 轉換後檢查 ----------

def check(src, out):
    """回傳錯誤清單。src 是轉換前、out 是轉換後的同一份檔案。"""
    errs = []
    han_names = [p.name for p in src.rglob("*") if p.is_file() and HAN.search(p.name)]
    for p in sorted((out / SCOPE).rglob("*")):
        rel = p.relative_to(out)
        if not in_scope(p, out): continue
        try: a, b = read(src / rel), read(p)
        except UnicodeDecodeError: continue
        errs += [f"{rel}：檔名「{n}」被轉掉了，要加進 phrases.tsv" for n in han_names if n in a and n not in b]
        if p.suffix in (".ts", ".tsx", ".js", ".json", ".css", ".py") and skeleton(a, fonts=True) != skeleton(b):
            errs.append(f"{rel}：中文以外的內容也被改了，轉換可能動到程式")
        if p.suffix == ".json":
            errs += [f"{rel}：{e}" for e in check_timeline(json.loads(a), json.loads(b))]
        if p.name == "edit.json" and (p.parent / "tl.json").exists():
            errs += [f"{rel}：{e}" for e in check_anchors(json.loads(a), json.loads(read(src / rel.parent / "tl.json")),
                                                          json.loads(b), json.loads(read(p.parent / "tl.json")))]
    return errs


def skeleton(s, fonts=False):
    """拿掉中文字、全形標點和引號之後剩下的部分。轉換前後應該一樣，只有字型名稱是故意換的。"""
    if fonts:
        for a, b in FONTS: s = s.replace(a, b)
    return re.sub(r"[一-鿿　-〿＀-￯“”‘’]", "", s)


def check_timeline(a, b):
    """有 chars 的段落用字元位置記時間，text 長度變了時間就會錯位。"""
    if isinstance(a, dict):
        errs = []
        if isinstance(a.get("chars"), dict) and isinstance(a.get("text"), str) and len(a["text"]) != len(b["text"]):
            errs.append(f"時間軸段落長度變了：「{a['text']}」→「{b['text']}」，在 phrases.tsv 加一條等長的詞")
        for x, y in zip(a.values(), b.values()): errs += check_timeline(x, y)
        return errs
    if isinstance(a, list):
        return [e for x, y in zip(a, b) for e in check_timeline(x, y)]
    return []


def check_anchors(edit_a, tl_a, edit_b, tl_b):
    """花字模板的時間錨點「段號:詞#第幾次」，轉換後要在同一段、同一個位置找得到。"""
    errs = []
    for x, y in zip(strings(edit_a), strings(edit_b)):
        m = re.match(r"^(\d+):(.+)$", x)
        if not m or m[2] == "end": continue
        n = int(m[1]) - 1
        if anchor_index(tl_a, n, x) != anchor_index(tl_b, n, y):
            errs.append(f"錨點「{x}」轉成「{y}」後位置對不上")
    return errs


def strings(v):
    if isinstance(v, dict): return [s for x in v.values() for s in strings(x)]
    if isinstance(v, list): return [s for x in v for s in strings(x)]
    return [v] if isinstance(v, str) else []


def anchor_index(tl, n, ref):
    segs = tl.get("segs") or []
    if n >= len(segs): return None
    word, _, nth = ref.split(":", 1)[1].partition("#")
    idx = -1
    for _ in range(int(nth or 1)): idx = segs[n]["text"].find(word, idx + 1)
    return idx


# ---------- git ----------

def git(*args, **kw):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, **kw)
    if r.returncode: sys.exit(f"git {' '.join(args)} 失敗：\n{r.stderr.strip()}")
    return r.stdout.strip()


def require_clean():
    if git("status", "--porcelain", "--untracked-files=no"):
        sys.exit("工作區有還沒 commit 的改動，先 commit 或 stash 再跑。")


def export(rev, dst):
    dst.mkdir(parents=True)
    archive = subprocess.run(["git", "archive", rev], cwd=ROOT, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dst)], input=archive, check=True)


def build():
    require_clean()
    if git("rev-parse", "--abbrev-ref", "HEAD") == TARGET:
        sys.exit(f"現在在 {TARGET}，先 git switch {SOURCE} 再跑（{TARGET} 由這個工具產生，不手改）。")
    src_sha, tgt_sha = git("rev-parse", SOURCE), git("rev-parse", TARGET)
    foreign = [c for c in git("rev-list", TARGET, f"^{SOURCE}").split() if TRAILER + ":" not in git("log", "-1", "--format=%B", c)]
    if foreign:
        sys.exit(f"{TARGET} 上有不是這個工具產生的 commit，產生新版會蓋掉它們。先把改動搬到 {SOURCE}，再刪掉這些 commit：\n"
                 + git("log", "--oneline", "--no-walk", *foreign))
    with tempfile.TemporaryDirectory() as td:
        src, out = Path(td) / "src", Path(td) / "out"
        export(SOURCE, src); export(SOURCE, out)
        convert_tree(out)
        errs = check(src, out)
        if errs: sys.exit("轉換後檢查沒過：\n" + "\n".join(errs))
        tree = write_tree(out, Path(td) / "index")
    if tree == git("rev-parse", f"{TARGET}^{{tree}}"):
        print(f"{TARGET} 已經是最新的，不用產生新 commit。"); return
    parents = ["-p", tgt_sha] + ([] if is_ancestor(src_sha, tgt_sha) else ["-p", src_sha])
    msg = f"Generate Traditional Chinese from {SOURCE} {src_sha[:7]}\n\n{TRAILER}: {src_sha}\n"
    new = git("commit-tree", tree, *parents, "-m", msg)
    git("update-ref", f"refs/heads/{TARGET}", new, tgt_sha)
    print(f"{TARGET} → {new[:7]}（{git('diff', '--shortstat', tgt_sha, new)}）")
    print(f"檢查：git diff {tgt_sha[:7]} {TARGET}　推上去：git push origin {SOURCE} {TARGET}")


def write_tree(work, index):
    """用暫存的 index 把 work 目錄寫成 git tree，不動目前的工作區。-f 是因為 archive 只有已追蹤的檔案。"""
    env = {**os.environ, "GIT_INDEX_FILE": str(index), "GIT_DIR": str(ROOT / ".git"), "GIT_WORK_TREE": str(work)}
    subprocess.run(["git", "add", "-A", "-f", "."], cwd=work, env=env, check=True)
    return subprocess.run(["git", "write-tree"], cwd=work, env=env, capture_output=True, text=True, check=True).stdout.strip()


def is_ancestor(a, b):
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=ROOT).returncode == 0


def sync():
    require_clean()
    git("fetch", "upstream")
    new = git("log", "--oneline", f"{SOURCE}..{UPSTREAM}")
    print("上游的新 commit：\n" + new if new else "上游沒有新 commit。")
    if git("rev-parse", "--abbrev-ref", "HEAD") != SOURCE: git("switch", SOURCE)
    if new:
        r = subprocess.run(["git", "merge", "--no-edit", UPSTREAM], cwd=ROOT)
        if r.returncode:
            sys.exit(f"合併有衝突。解決衝突、git commit 之後，再跑 python3 tools/zhtw/zhtw.py build。")
    build()


# ---------- 檢查用語 ----------

def terms(paths):
    """列出 opencc 用台灣詞彙換掉的詞（s2tw 只轉字、s2twp 連詞彙一起轉，兩者的差異），已在 phrases.tsv 的不列。"""
    if not paths:
        last = re.search(rf"{TRAILER}: (\w+)", git("log", "-1", "--format=%B", TARGET))
        names = git("diff", "--name-only", f"{last[1]}..{SOURCE}", "--", SCOPE) if last else git("ls-files", SCOPE)
        paths = [p for p in names.split("\n") if p and (not p.endswith(SKIP_SUFFIX) or p in CONTENT_PY)]
    phrases, seen = load_phrases(), {}
    for f in paths:
        try: text, _ = protect(read(ROOT / f), phrases)
        except (UnicodeDecodeError, FileNotFoundError): continue
        if not HAN.search(text): continue
        a, b = opencc("s2tw", text), opencc("s2twp", text)
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op != "equal":
                k = (a[max(0, i1 - 2):i2 + 2], b[max(0, j1 - 2):j2 + 2])
                seen.setdefault(k, f)
    for (x, y), f in sorted(seen.items(), key=lambda kv: kv[1]):
        print(f"{x} → {y}    {f}")
    print(f"共 {len(seen)} 處。換錯的就在 phrases.tsv 加一條簡體原詞。", file=sys.stderr)


if __name__ == "__main__":
    main()
