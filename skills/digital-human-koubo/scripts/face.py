"""脸部关键点（MediaPipe Face Landmarker），make_anchors.py 和 warp_eyes.py 共用。
- 模型第一次用时下载到 ~/.cache/digital-human-koubo/face_landmarker.task（约 3.6 MB，Apache 2.0）
- 要 mediapipe 和 opencv，用 uv 临时装：uv run --no-project --with mediapipe --with opencv-python-headless python scripts/<脚本> …"""
import urllib.request
from pathlib import Path

import cv2, mediapipe as mp, numpy as np
from mediapipe.tasks.python import BaseOptions, vision

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL = Path.home() / ".cache" / "digital-human-koubo" / "face_landmarker.task"
# face mesh 的点号：每只眼两个眼角、三对上下眼皮；上下唇内缘；鼻尖
EYES = [dict(corners=(33, 133), lids=((159, 145), (158, 153), (160, 144))),
        dict(corners=(362, 263), lids=((386, 374), (385, 380), (387, 373)))]
LIPS, NOSE = (13, 14), 1
_landmarker = None

def landmarks(bgr):
    """一张 BGR 图 → 478 个点的像素坐标；没有脸回 None"""
    global _landmarker
    if _landmarker is None:
        if not MODEL.exists():
            MODEL.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, MODEL)
        _landmarker = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(MODEL)), num_faces=1))
    r = _landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
    if not r.face_landmarks: return None
    h, w = bgr.shape[:2]
    return np.array([(p.x * w, p.y * h) for p in r.face_landmarks[0]])

def eye_geometry(pts):
    """每只眼：中心、眼宽、眼高（三对眼皮的平均）"""
    out = []
    for e in EYES:
        a, b = pts[e["corners"][0]], pts[e["corners"][1]]
        out.append(dict(center=(a + b) / 2, width=np.linalg.norm(a - b),
                        height=np.mean([np.linalg.norm(pts[u] - pts[d]) for u, d in e["lids"]])))
    return out

def pose(pts):
    """头的位置和表情：两眼中点、两眼距离、眼高比（眼高÷两眼距离）、张嘴比、歪头角度（度）、转头（鼻尖相对两眼中点的水平偏移÷两眼距离）"""
    g = eye_geometry(pts)
    c0, c1 = g[0]["center"], g[1]["center"]
    iod = np.linalg.norm(c1 - c0); mid = (c0 + c1) / 2
    return dict(center=mid, iod=iod, eye=np.mean([x["height"] for x in g]) / iod,
                mouth=np.linalg.norm(pts[LIPS[0]] - pts[LIPS[1]]) / iod,
                roll=float(np.degrees(np.arctan2(c1[1] - c0[1], c1[0] - c0[0]))), turn=(pts[NOSE][0] - mid[0]) / iod)
