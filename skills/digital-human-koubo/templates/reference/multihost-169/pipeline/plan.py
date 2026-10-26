import json, math
PCT=0.35   # 每秒佔 grok 每週額度的上限估算（720p 2026-10 實測 0.25–0.35%；480p 沒實測，按 720p 估）
def d(t): return min(15, math.ceil(len(t)/5.4+1))
# host: tank=白背心(9:16, avatar_ref.jpg)  me=使用者本人(16:9, me_polo.jpg)
NEW=[
 # 冷開場：多語言快閃（也用於「升級一」六宮格）
 ("L_en","冷開場","tank","full","Hi! I'm an AI digital human, and I can speak your language.",5,"English"),
 ("L_ja","冷開場","tank","full","こんにちは！私はAIデジタルヒューマンです。",5,"Japanese"),
 ("L_ko","冷開場","tank","full","안녕하세요! 저는 AI 디지털 휴먼이에요.",5,"Korean"),
 ("L_fr","冷開場","tank","full","Bonjour ! Je suis une humaine numérique créée par l'IA.",5,"French"),
 ("L_es","冷開場","me","full","¡Hola! Soy un humano digital hecho con IA.",5,"Spanish"),
 ("L_ar","冷開場","me","full","مرحباً! أنا إنسان رقمي صنعه الذكاء الاصطناعي.",5,"Arabic"),
 ("t1","開場","tank","full","上一期，我教你做出了我。這一期升級：讓數位人說外語、進場景、換角色，還請來一位新同事。",None,"Mandarin"),
 ("t2","開場","tank","full","老規矩，先用一分半鐘，把基礎三步過一遍。",None,"Mandarin"),
 ("t3","基礎·聲音","tank","pip","上期還留了一個坑：換了聲音，口型就對不準。接下來，請我的同事接棒。",None,"Mandarin"),
 ("u1","換人","me","full","大家好，我是她的同事，也是數位人。不一樣的是，我是用我本人的一張照片做的。",None,"Mandarin"),
 ("u2","換人","me","full","你看這張照片：橫式、正臉、背景乾淨。橫式照片，直接就能生成橫式口播。",None,"Mandarin"),
 ("u3","換人","me","pip","先說那個坑。Grok 的口型，跟的是它自己的聲音。所以最穩的做法，是直接讓它用目標語言開口。",None,"Mandarin"),
 ("u4","換人","me","pip","如果一定要用你自己的錄音，就換一個音訊驅動口型的模型，比如 OmniHuman：一張照片，加一段錄音。",None,"Mandarin"),
 ("u5","升級①多語言","me","full","升級一，多語言。想讓數位人說英語、日語、韓語，只要在提示詞裡寫清楚語言，台詞直接用那門語言寫。",None,"Mandarin"),
 ("u6","升級①多語言","me","pip","注意，別寫中文讓它自己翻，要提前翻好。生成完，再用語音識別回聽一遍，確認沒念錯。",None,"Mandarin"),
 ("u7","升級②進場景","me","full","升級二，進場景。同一個數位人，可以去直播間帶貨、拍產品廣告、做旅遊導覽、當講師。",None,"Mandarin"),
 ("u8","升級②進場景","me","pip","方法是兩步。第一步，把人物照片和場景描述一起發給圖片模型，合成一張開場畫面。",None,"Mandarin"),
 ("u9","升級②進場景","me","pip","比如：讓她站在直播間裡，手裡拿著一瓶精華。人物不變，只換背景、服裝和道具。",None,"Mandarin"),
 ("u10","升級②進場景","me","pip","第二步，把這張畫面交給 Grok，寫好台詞，它就開口了。我們來看看效果。",None,"Mandarin"),
 ("u11","升級②進場景","me","pip","帶貨、廣告、導覽、講課，一張照片全搞定。商用之前，記得標註 AI 生成。",None,"Mandarin"),
 ("t4","升級③換角色","tank","full","升級三，換角色。誰說數位人一定是人？小貓小狗，也能開口。",None,"Mandarin"),
 ("t5","升級③換角色","tank","pip","做法一樣：先生成角色形象，再寫台詞。提示詞裡寫清楚，是這隻貓在說話，嘴巴要跟著動。",None,"Mandarin"),
 ("u12","流程","me","full","最後，把這些串成一條片子。還是那套流程：腳本、Skill、剪輯。",None,"Mandarin"),
]
SCENES=[ # 先用 grok 的 image_edit 合成開場畫面（stills/<id>.jpg），再 Grok 開口
 ("S_shop","tank","9:16",8,"直播間帶貨","家人們看過來！這瓶精華一滴就能推開，今天直播間下單，再送小樣！","Mandarin"),
 ("S_ad","me","16:9",6,"產品廣告","Forty hours of battery. Zero cables. Just press play.","English"),
 ("S_travel","tank","9:16",7,"旅遊導覽（京都）","ここは京都の祇園です。夜の提灯、とてもきれいでしょう？","Japanese"),
 ("S_class","me","16:9",7,"課程講師","今天這節課，我們用三分鐘，搞懂什麼是大語言模型。","Mandarin"),
 ("S_cat","cat","9:16",7,"橘貓店長帶貨貓糧","喵～這罐貓糧，本喵親自試吃過，好吃到舔盤！","Mandarin"),
 ("S_dog","dog","16:9",7,"柴犬新聞主播","Good evening. Breaking news: the park is now open for belly rubs.","English"),
 ("S_duo","duo","16:9",9,"結尾：兩位同框","照片、語言、場景、角色，你想到的，數位人都能演。去組建你自己的數位人團隊吧，下期見！","Mandarin"),
]
REUSE=["s1a","s1b","s1c","s1d","s1e","s2a","s2b","s2c","s2d","s2e","s3a","s3b","s4b","s4c","s4d","s6b","s6c","s7b","s7c"]
rows=[];tot=0
for i,ch,h,shot,t,dur,lang in NEW:
    dur=dur or d(t); res="720p" if shot=="full" else "480p"; c=round(dur*PCT,2); tot+=c
    rows.append(dict(id=i,ch=ch,host=h,shot=shot,t=t,dur=dur,res=res,lang=lang,cost=c))
for i,h,r,dur,name,t,lang in SCENES:
    c=round(dur*PCT,2); tot+=c
    rows.append(dict(id=i,ch="場景" if i!="S_duo" else "結尾",host=h,shot="scene",ratio=r,scene=name,t=t,dur=dur,res="720p",lang=lang,cost=c))
json.dump(dict(new=rows,reuse=REUSE,total=round(tot,2)),open("plan.json","w"),ensure_ascii=False,indent=1)   # cost / total：佔每週額度的百分比（上限估算）
nv=sum(r["dur"] for r in rows)
print("新生成口播/片段",len(rows),"段",nv,f"秒；影片約佔每週額度 {tot:.0f}%（上限估算），另有",len(SCENES),"張場景圖（image_edit，額度沒實測）")
for k in ["tank","me","cat","dog","duo"]:
    print(k, f"{sum(r['cost'] for r in rows if r['host']==k):.1f}%", sum(r["dur"] for r in rows if r["host"]==k),"s")
