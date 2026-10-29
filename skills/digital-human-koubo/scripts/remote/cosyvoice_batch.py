"""在 GPU 机器上跑的配音批次：CosyVoice 3 零样本克隆，一段一个 wav。
tts_generate.py 每次把这个文件、job.json 和参考音档一起传过去，用 CosyVoice 3 环境的 python 执行：
  python cosyvoice_batch.py job.json
输出 out/<段 id>.wav，每段印一行 KOUBO_TTS {json} 给 tts_generate.py 读。"""
import json, os, random, sys

job_path = os.path.abspath(sys.argv[1])
base = os.path.dirname(job_path)
job = json.load(open(job_path, encoding="utf-8"))
repo = os.path.expanduser(job["repo"])
os.chdir(repo)   # model_dir 是相对 repo 的路径
sys.path[:0] = [repo, repo + "/third_party/Matcha-TTS"]
import numpy as np, torch, torchaudio
from cosyvoice.cli.cosyvoice import AutoModel

PREFIX = "You are a helpful assistant.<|endofprompt|>"   # CosyVoice 3 的 zero-shot 要在参考逐字稿前加这段（官方 example.py）
cv = AutoModel(model_dir=job["model_dir"])
os.makedirs(os.path.join(base, "out"), exist_ok=True)
for s in job["segments"]:
    seed = job["seed"]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    parts = [o["tts_speech"] for o in cv.inference_zero_shot(s["text"], PREFIX + s["ref_text"], os.path.join(base, s["ref_wav"]), stream=False)]
    wav = torch.cat(parts, dim=1)
    torchaudio.save(os.path.join(base, "out", s["id"] + ".wav"), wav.cpu(), cv.sample_rate)
    print("KOUBO_TTS", json.dumps({"id": s["id"], "sec": round(wav.shape[1] / cv.sample_rate, 2)}), flush=True)
