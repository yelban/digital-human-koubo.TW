"""plan.json → tasks.json（grok_generate.py 的输入）。参考图是工程里的本机文件，提示词用 <IMAGE_0> 指它"""
import json, sys
from pathlib import Path
P=json.load(open('plan.json'))
REF={'tank':'refs/avatar_ref.jpg','me':'refs/me_polo.jpg'}   # 主播参考图：tank 从技能的 assets/ 复制，me 是用户本人照片
STILL={k:f'stills/{k}.jpg' for k in ('S_shop','S_ad','S_travel','S_class','S_cat','S_dog','S_duo')}   # 场景段的开场画面，先用 grok 的 image_edit 合成
PCT=(0.25,0.35)   # 720p 每秒占 grok 每周额度（2026-10 实测）；480p 没实测，按 720p 估
TANK_V="young friendly female voice, clear and patient but lively, natural pace"
ME_V="warm, steady, confident male voice around 35 years old, natural pace"
ACT={'full':"warm eye contact, expressive face, natural hand gestures",
     'pip':"calm explaining tone, small nods, occasionally glancing down as if reading a screen, small pointing gestures"}
def lang_name(l): return {"Mandarin":"Mandarin Chinese"}.get(l,l)
def narr(r):
    if r['host']=='tank':
        ref=REF['tank']; who=f"The young woman in <IMAGE_0> talks straight into her phone's front camera, same selfie framing, lighting and outfit as the reference, like a friendly tech vlogger presenting a tutorial"
        pron,v,ratio="She",TANK_V,"9:16"
    else:
        ref=REF['me']; who=f"The man in <IMAGE_0> talks straight to the camera, same framing, gray studio backdrop, navy polo shirt, glasses and soft lighting as the reference, like a friendly tech blogger presenting a tutorial"
        pron,v,ratio="He",ME_V,"16:9"
    cam="Handheld selfie feel with only a very slight natural sway." if r['host']=='tank' else "Locked-off camera, no zoom."
    act=ACT['full' if r['shot']=='full' else 'pip']
    if r['id'].startswith('L_'): act="bright friendly greeting, a small wave at the start, warm smile"
    p=(f"{who}: {act}. {cam} {pron} speaks {lang_name(r['lang'])}, clearly lip-synced, in a {v}:\n“{r['t']}”\n"
       f"Sound: only {'her' if pron=='She' else 'his'} voice and quiet room tone, no music, no subtitles, no on-screen text.")
    return dict(id=r['id'],prompt=p,images=[ref],aspect_ratio=ratio,duration=r['dur'],resolution_name=r['res'])
SC={
 'S_shop':("The young woman in <IMAGE_0> is a cheerful livestream shopping host: she holds the serum bottle up to the camera, then gestures toward it with her other hand, lively and persuasive, bright eyes, natural head movement. Static phone camera.","She","young bright energetic female voice, fast upbeat livestream-host pace"),
 'S_ad':("The man in <IMAGE_0> presents the earbuds in a polished product commercial: he lifts the open case slightly toward the lens, confident smile, then a small nod. Slow gentle push-in.","He","confident, smooth male commercial voice-over tone"),
 'S_travel':("The young woman in <IMAGE_0> is a travel vlogger filming herself in Gion at dusk, the lanterns glowing behind her; she glances back at the lane once, then smiles into the lens. Handheld selfie walk, very slight sway.","She","soft, cheerful young female voice, relaxed travel-vlog pace"),
 'S_class':("The man in <IMAGE_0> is a teacher at the whiteboard: he taps the diagram with the marker, then turns to the camera and explains with a friendly open-hand gesture. Static camera.","He","warm, clear male teacher voice, steady pace"),
 'S_cat':("The orange cat in <IMAGE_0> talks to the camera like a shop manager presenting a product: its mouth clearly opens and closes in sync with the words, ears twitch, it pats the can of cat food with one paw, cute expressive face. Static camera.","It","cute, playful small high-pitched voice"),
 'S_dog':("The Shiba Inu in <IMAGE_0> reads the evening news like a TV anchor: its mouth clearly opens and closes in sync with the words, serious expression, a slight head tilt at the end. Static broadcast camera.","It","deep, serious male TV news-anchor voice"),
 'S_duo':("The woman and the man in <IMAGE_0> co-host the ending of a show: she speaks the line to the camera while he smiles and nods; at the very end both wave goodbye together. Static camera.","She","young friendly female voice, clear and patient but lively, natural pace"),
}
def scene(r):
    a,pron,v=SC[r['id']]
    p=(f"{a} {pron} speaks {lang_name(r['lang'])}, clearly lip-synced, in a {v}:\n“{r['t']}”\n"
       "Sound: only the voice and quiet room tone, no music, no subtitles, no on-screen text.")
    return dict(id=r['id'],prompt=p,images=[STILL[r['id']]],aspect_ratio=r['ratio'],duration=r['dur'],resolution_name="720p")
T=[]
for r in P['new']:
    if r['id']=='u1': continue
    T.append(scene(r) if r['shot']=='scene' else narr(r))
missing=sorted({i for t in T for i in t['images'] if not Path(i).exists()})
for t in T: t['images']=[str(Path(i).resolve()) for i in t['images']]
json.dump(T,open('tasks.json','w'),ensure_ascii=False,indent=1)
secs=sum(t['duration'] for t in T)
print(f"{len(T)} 段 · {secs} 秒 · 预估占 grok 每周额度 {secs*PCT[0]:.0f}–{secs*PCT[1]:.0f}%（不含 image_edit 合成场景图，那部分没实测）")
print(T[0]['prompt']); print(T[-1]['prompt'])
if missing: sys.exit(f"⚠ 这些参考图还没有，做好再跑 grok_generate.py：{'、'.join(missing)}")
